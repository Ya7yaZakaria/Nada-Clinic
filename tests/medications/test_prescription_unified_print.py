from tests.factories import create_drug_via_service as create_drug
from tests.factories import create_user
from tests.factories import create_visit_with_pelvic_pain as create_visit
from tests.factories import login_follow_redirects as login
from tests.factories import make_app_csrf_disabled as make_app

from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.print_template import PrintTemplate
from app.models.drug import Drug
from app.models.drug_dictionary import DrugForm, DrugRoute
from app.services.drug_service import DrugService
from app.services.patient_service import PatientService
from app.services.prescription_service import PrescriptionService
from app.services.print_template_service import PrintTemplateService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01099220000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)

def create_prescription_with_item(visit):
    drug, route = create_drug()
    prescription = PrescriptionService.create_prescription(visit=visit)
    PrescriptionService.add_item(
        prescription=prescription,
        drug=drug,
        dose="1 tablet",
        frequency="Every 24 hours",
        duration="5 days",
        instructions_ar="Arabic instructions",
        route=route,
    )
    return prescription


def test_unified_prescription_preview_uses_default_print_template():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-unified-print@example.com", "01099220001", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        create_prescription_with_item(visit)

        client = app.test_client()
        login(client, "doctor-unified-print@example.com")

        response = client.get(f"/print/prescriptions/{visit.uuid}/preview")

        assert response.status_code == 200
        assert b"Unified Prescription Print" in response.data
        assert b"Default Prescription Layout" in response.data
        assert b"Tavanic" in response.data
        assert b"Arabic instructions" in response.data
        assert visit.patient.formatted_mrn.encode("utf-8") in response.data
        assert b"diagnosis" not in response.data.lower()

        db.drop_all()


def test_unified_prescription_designer_redirects_to_preview():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-unified-designer@example.com", "01099220002", "Doctor")
        patient = create_patient(phone_primary="01099220102")
        visit = create_visit(patient)
        create_prescription_with_item(visit)

        client = app.test_client()
        login(client, "doctor-unified-designer@example.com")

        response = client.get(
            f"/print/prescriptions/{visit.uuid}/designer",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Unified Prescription Print" in response.data
        assert b"Prescription uses the unified print template" in response.data

        db.drop_all()


def test_unified_prescription_preview_accepts_custom_template():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-unified-custom-template@example.com", "01099220003", "Doctor")
        patient = create_patient(phone_primary="01099220103")
        visit = create_visit(patient)
        create_prescription_with_item(visit)

        template = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
            name="Custom Rx Paper",
            paper_width_mm=100,
            paper_height_mm=140,
            layout_json={
                "patient_name": {"x": 10, "y": 10, "width": 40, "height": 8, "fontSize": 12, "visible": True},
                "prescription_items": {"x": 10, "y": 35, "width": 80, "height": 80, "fontSize": 14, "lineHeight": 8, "visible": True},
            },
        )

        client = app.test_client()
        login(client, "doctor-unified-custom-template@example.com")

        response = client.get(
            f"/print/prescriptions/{visit.uuid}/preview?template_uuid={template.uuid}"
        )

        assert response.status_code == 200
        assert b"Custom Rx Paper" in response.data
        assert b"Tavanic" in response.data

        db.drop_all()


def test_unified_prescription_preview_redirects_when_no_prescription_exists():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-unified-empty@example.com", "01099220004", "Doctor")
        patient = create_patient(phone_primary="01099220104")
        visit = create_visit(patient)
        create_drug()

        client = app.test_client()
        login(client, "doctor-unified-empty@example.com")

        response = client.get(
            f"/print/prescriptions/{visit.uuid}/preview",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"No prescription exists for this visit" in response.data

        db.drop_all()


def test_reception_cannot_open_unified_prescription_preview():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-unified-print@example.com", "01099220005", "Reception")
        patient = create_patient(phone_primary="01099220105")
        visit = create_visit(patient)
        create_prescription_with_item(visit)

        client = app.test_client()
        login(client, "reception-unified-print@example.com")

        response = client.get(f"/print/prescriptions/{visit.uuid}/preview")

        assert response.status_code == 403

        db.drop_all()
