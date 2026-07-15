from datetime import date, timedelta
from io import BytesIO

from app import create_app
from app.extensions import db
from app.models import Patient, PatientDocument, Prescription, User, Visit
from app.models.drug import Drug
from app.models.drug_dictionary import DrugForm, DrugRoute
from app.models.partner import PartnerSemenAnalysis
from app.services.patient_service import PatientService
from app.services.partner_semen_analysis_service import PartnerSemenAnalysisService
from app.services.partner_service import PartnerService
from app.services.prescription_service import PrescriptionService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
        PATIENT_DOCUMENT_MAX_FILE_SIZE_BYTES=1024 * 1024,
    )
    return app


def create_user(email, phone, role_name):
    user = User(email=email, phone=phone, name=role_name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()
    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)
    return user


def login(client, email):
    return client.post(
        "/auth/login",
        data={"login_identifier": email, "password": "12345678"},
        follow_redirects=True,
    )


def create_patient(phone="01088000000"):
    return PatientService.create_patient(
        name_ar="Ù…Ù†Ù‰ Ø¹Ù„ÙŠ",
        name_en="Mona Ali",
        phone_primary=phone,
        date_of_birth=date(1994, 1, 1),
    )


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="infertility",
        chief_complaint="Primary infertility",
        plan="Start workup.",
    )


def create_drug():
    form = DrugForm(code="tab", name_en="Tablet", name_ar="Ù‚Ø±Øµ", is_active=True)
    route = DrugRoute(code="oral", name_en="Oral", name_ar="ÙÙ…ÙˆÙŠ", is_active=True)
    db.session.add_all([form, route])
    db.session.commit()

    drug = Drug(
        generic_name="Vitamin E",
        trade_name="Vitamin E",
        strength="400 IU",
        form=form,
        route=route,
        is_active=True,
    )
    db.session.add(drug)
    db.session.commit()
    return drug


def setup_context(email="doctor-partner@example.com", phone="01088000001", role="Doctor"):
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        user = create_user(email, phone, role)
        patient = create_patient()
        visit = create_visit(patient)
        drug = create_drug()
        yield app, user, patient, visit, drug
        db.drop_all()


def test_partner_service_one_active_partner_and_update():
    for app, doctor, patient, visit, drug in setup_context():
        partner = PartnerService.create_partner(
            patient=patient,
            name="Ahmed Mohamed",
            phone="01012345678",
            age_years=34,
            occupation="Engineer",
            previous_children="No previous children",
            fertility_notes="Primary infertility 3 years",
            medical_notes="No chronic disease",
            follow_up_note="Repeat SA after 3 months",
            follow_up_date=date.today() + timedelta(days=90),
        )

        assert partner.patient_id == patient.id
        assert PartnerService.get_patient_partner(patient).id == partner.id

        try:
            PartnerService.create_partner(patient=patient, name="Second Partner")
            assert False, "Expected one active partner validation"
        except ValueError as exc:
            assert "already has an active partner" in str(exc)

        PartnerService.update_partner(
            partner,
            name="Ahmed Zaki",
            phone="01000000000",
            age_years=35,
            occupation="Doctor",
            previous_children="One child from previous marriage",
            fertility_notes="Low motility noted before",
            medical_notes="None",
            follow_up_note="Review after SA",
            follow_up_date=date.today(),
        )
        assert partner.name == "Ahmed Zaki"
        assert partner.age_years == 35


def test_partner_semen_analysis_notes_and_upload_document():
    for app, doctor, patient, visit, drug in setup_context("doctor-partner-sa@example.com", "01088000002"):
        partner = PartnerService.create_partner(patient=patient, name="Ahmed Mohamed")

        notes_only = PartnerSemenAnalysisService.create_analysis(
            partner=partner,
            analysis_date=date.today() - timedelta(days=30),
            notes="Old SA: low motility.",
            actor_user=doctor,
        )
        assert notes_only.document_id is None

        client = app.test_client()
        login(client, "doctor-partner-sa@example.com")

        response = client.post(
            f"/partners/{partner.uuid}/semen-analysis/new",
            data={
                "analysis_date": date.today().isoformat(),
                "notes": "Latest SA uploaded as image.",
                "file": (BytesIO(b"fake image content"), "sa.jpg"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Latest SA uploaded as image" in response.data

        latest = PartnerSemenAnalysisService.latest_for_partner(partner)
        assert latest.document is not None
        assert latest.document.document_type == PatientDocument.TYPE_SEMEN_ANALYSIS
        assert PartnerSemenAnalysis.query.filter_by(partner_id=partner.id, is_active=True).count() == 2


def test_partner_prescription_uses_existing_prescription_items_and_visit_prescription_still_works():
    for app, doctor, patient, visit, drug in setup_context("doctor-partner-rx@example.com", "01088000003"):
        partner = PartnerService.create_partner(patient=patient, name="Ahmed Mohamed")

        partner_prescription = PrescriptionService.create_partner_prescription(
            partner=partner,
            notes="Male factor support",
            actor_user=doctor,
        )
        assert partner_prescription.prescription_target == Prescription.TARGET_PARTNER
        assert partner_prescription.partner_id == partner.id
        assert partner_prescription.visit_id is None
        assert partner_prescription.patient_id == patient.id

        item = PrescriptionService.add_item(
            prescription=partner_prescription,
            drug=drug,
            dose="One tablet",
            frequency="Once daily",
            duration="3 months",
            instructions_ar="Ù‚Ø±Øµ ÙŠÙˆÙ…ÙŠØ§ Ù„Ù…Ø¯Ø© Ù£ Ø´Ù‡ÙˆØ±",
        )
        assert item.prescription_id == partner_prescription.id
        assert PrescriptionService.list_items(partner_prescription)[0].drug_id == drug.id

        visit_prescription = PrescriptionService.get_or_create_prescription(
            visit=visit,
            actor_user=doctor,
        )
        assert visit_prescription.prescription_target == Prescription.TARGET_PATIENT
        assert visit_prescription.partner_id is None
        assert visit_prescription.visit_id == visit.id


def test_partner_workspace_ui_and_partner_prescription_routes():
    for app, doctor, patient, visit, drug in setup_context("doctor-partner-ui@example.com", "01088000004"):
        client = app.test_client()
        login(client, "doctor-partner-ui@example.com")

        response = client.get(f"/patients/{patient.uuid}", follow_redirects=True)
        assert response.status_code == 200
        assert b"Partner / Husband" in response.data
        assert b"Add Partner" in response.data

        response = client.post(
            f"/patients/{patient.uuid}/partner/new",
            data={
                "name": "Ahmed Mohamed",
                "phone": "01012345678",
                "age_years": 34,
                "occupation": "Engineer",
                "previous_children": "No previous children",
                "fertility_notes": "Primary infertility",
                "medical_notes": "None",
                "follow_up_note": "Repeat SA",
                "follow_up_date": date.today().isoformat(),
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Ahmed Mohamed" in response.data
        assert b"Write Partner Prescription" in response.data

        partner = PartnerService.get_patient_partner(patient)

        response = client.post(
            f"/partners/{partner.uuid}/prescriptions/new",
            data={"notes": "Partner vitamins"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Partner Prescription" in response.data

        prescription = PrescriptionService.list_partner_prescriptions(partner)[0]
        response = client.post(
            f"/partners/prescriptions/{prescription.uuid}/items",
            data={
                "drug_id": drug.id,
                "route_id": 0,
                "dose": "One tablet",
                "frequency": "Once daily",
                "duration": "3 months",
                "instructions_ar": "Ù‚Ø±Øµ ÙŠÙˆÙ…ÙŠØ§",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Medication added to partner prescription" in response.data
        assert b"Vitamin E" in response.data


def test_reception_blocked_from_partner_workflows():
    for app, reception, patient, visit, drug in setup_context("reception-partner@example.com", "01088000005", "Reception"):
        client = app.test_client()
        login(client, "reception-partner@example.com")

        response = client.get(f"/patients/{patient.uuid}/partner/new", follow_redirects=True)
        assert response.status_code == 403

        partner = PartnerService.create_partner(patient=patient, name="Ahmed Mohamed")
        response = client.get(f"/partners/{partner.uuid}", follow_redirects=True)
        assert response.status_code == 403

