from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.drug import Drug
from app.models.drug_dictionary import DrugForm, DrugRoute
from app.models.prescription import PrescriptionItem
from app.services.drug_service import DrugService
from app.services.patient_service import PatientService
from app.services.prescription_service import PrescriptionService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
    )
    return app


def create_user(email, phone, role_name, name="Test User"):
    user = User(email=email, phone=phone, name=name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)
    return user


def login(client, email):
    return client.post(
        "/auth/login",
        data={
            "login_identifier": email,
            "password": "12345678",
        },
        follow_redirects=True,
    )


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01099110000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Pelvic pain",
    )


def create_drug():
    form = DrugForm(code="tablet", name_en="Tablet")
    route = DrugRoute(code="oral", name_en="Oral")
    db.session.add_all([form, route])
    db.session.commit()

    drug = DrugService.create_drug(
        generic_name="Levofloxacin",
        trade_name="Tavanic",
        strength="500 mg",
        form=form,
        route=route,
    )
    return drug, route


def test_doctor_sees_prescription_section_in_visit_detail():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-prescription-ui@example.com", "01099110001", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        create_drug()

        client = app.test_client()
        login(client, "doctor-prescription-ui@example.com")

        response = client.get(f"/visits/{visit.uuid}")

        assert response.status_code == 200
        assert b"Structured prescription" in response.data
        assert b"Add medication" in response.data

        db.drop_all()


def test_reception_cannot_open_visit_detail_or_prescription_section():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-prescription-ui@example.com", "01099110002", "Reception")
        patient = create_patient()
        visit = create_visit(patient)
        create_drug()

        client = app.test_client()
        login(client, "reception-prescription-ui@example.com")

        response = client.get(f"/visits/{visit.uuid}")

        assert response.status_code == 403

        db.drop_all()


def test_doctor_can_add_prescription_item_from_visit_detail():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-add-prescription-item@example.com", "01099110003", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        drug, route = create_drug()

        client = app.test_client()
        login(client, "doctor-add-prescription-item@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/prescription/items",
            data={
                "drug_id": str(drug.id),
                "route_id": "0",
                "dose": "1 tablet",
                "frequency": "Every 24 hours",
                "duration": "5 days",
                "instructions_ar": "قرص مرة يوميًا لمدة ٥ أيام بعد الأكل",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Tavanic" in response.data
        assert "قرص مرة يوميًا".encode("utf-8") in response.data

        prescription = PrescriptionService.get_prescription_for_visit(visit)
        assert prescription is not None
        assert PrescriptionService.list_items(prescription)[0].drug_id == drug.id

        db.drop_all()


def test_reception_cannot_add_prescription_item():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-add-prescription-item@example.com", "01099110004", "Reception")
        patient = create_patient()
        visit = create_visit(patient)
        drug, _route = create_drug()

        client = app.test_client()
        login(client, "reception-add-prescription-item@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/prescription/items",
            data={
                "drug_id": str(drug.id),
                "dose": "1 tablet",
                "frequency": "Every 24 hours",
                "duration": "5 days",
                "instructions_ar": "تعليمات",
            },
        )

        assert response.status_code == 403

        db.drop_all()


def test_doctor_can_edit_prescription_item():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-edit-prescription-item@example.com", "01099110005", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        drug, route = create_drug()
        prescription = PrescriptionService.create_prescription(visit=visit)
        item = PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose="1 tablet",
            frequency="Once daily",
            duration="5 days",
            instructions_ar="تعليمات قديمة",
        )

        client = app.test_client()
        login(client, "doctor-edit-prescription-item@example.com")

        response = client.post(
            f"/prescription-items/{item.uuid}/edit",
            data={
                "drug_id": str(drug.id),
                "route_id": str(route.id),
                "dose": "2 tablets",
                "frequency": "Every 12 hours",
                "duration": "7 days",
                "instructions_ar": "قرصين كل ١٢ ساعة لمدة ٧ أيام",
            },
            follow_redirects=True,
        )

        db.session.refresh(item)

        assert response.status_code == 200
        assert item.dose == "2 tablets"
        assert item.frequency == "Every 12 hours"
        assert item.duration == "7 days"
        assert item.instructions_ar == "قرصين كل ١٢ ساعة لمدة ٧ أيام"

        db.drop_all()


def test_doctor_can_remove_prescription_item():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-remove-prescription-item@example.com", "01099110006", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        drug, _route = create_drug()
        prescription = PrescriptionService.create_prescription(visit=visit)
        item = PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose="1 tablet",
            frequency="Once daily",
            duration="5 days",
            instructions_ar="تعليمات",
        )
        item_uuid = item.uuid
        item_id = item.id

        client = app.test_client()
        login(client, "doctor-remove-prescription-item@example.com")

        response = client.post(
            f"/prescription-items/{item_uuid}/remove",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert db.session.get(PrescriptionItem, item_id) is None

        db.drop_all()
