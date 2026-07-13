from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.investigation import InvestigationOrder, InvestigationTest
from app.models.print_template import PrintTemplate
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_service import InvestigationService
from app.services.patient_service import PatientService
from app.services.print_template_service import PrintTemplateService
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
        "phone_primary": "01066440000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Investigation print visit",
    )


def create_investigation_test(code="amh", name="AMH", unit="ng/mL"):
    category = InvestigationDictionaryService.create_category(
        code=f"{code}_category",
        name_en=f"{name} Category",
    )
    return InvestigationDictionaryService.create_test(
        code=code,
        name_en=name,
        category=category,
        default_unit=unit,
        default_reference_range="0.4-4.0",
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def create_order_with_item(patient=None, visit=None):
    if patient is None:
        patient = create_patient()
    if visit is None:
        visit = create_visit(patient)

    test = create_investigation_test()
    order = InvestigationService.create_order(
        patient=patient,
        ordered_visit=visit,
        priority=InvestigationOrder.PRIORITY_IMPORTANT,
        order_notes="Second day cycle workup",
    )
    InvestigationService.add_order_item(
        order=order,
        test=test,
        item_notes="Morning sample",
    )
    return order


def test_unified_investigation_preview_uses_default_template():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-investigation-print@example.com", "01066440001", "Doctor")
        order = create_order_with_item()

        client = app.test_client()
        login(client, "doctor-investigation-print@example.com")

        response = client.get(f"/print/investigations/{order.uuid}/preview")

        assert response.status_code == 200
        assert b"Unified Investigation Request Print" in response.data
        assert b"Default Investigation Request Layout" in response.data
        assert b"AMH" in response.data
        assert b"Morning sample" in response.data
        assert order.patient.formatted_mrn.encode("utf-8") in response.data
        assert "ثاني أيام الدورة".encode("utf-8") in response.data
        assert b"result" not in response.data.lower()

        db.drop_all()


def test_unified_investigation_designer_redirects_to_preview():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-investigation-designer@example.com", "01066440002", "Doctor")
        order = create_order_with_item()

        client = app.test_client()
        login(client, "doctor-investigation-designer@example.com")

        response = client.get(
            f"/print/investigations/{order.uuid}/designer",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Unified Investigation Request Print" in response.data
        assert b"Investigation request uses the unified print template" in response.data

        db.drop_all()


def test_unified_investigation_preview_accepts_custom_template():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-investigation-custom-template@example.com", "01066440003", "Doctor")
        order = create_order_with_item()

        template = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST,
            name="Custom Investigation Paper",
            paper_width_mm=100,
            paper_height_mm=140,
            layout_json={
                "patient_name": {"x": 10, "y": 10, "width": 40, "height": 8, "fontSize": 12, "visible": True},
                "instruction": {"x": 10, "y": 25, "width": 80, "height": 8, "fontSize": 14, "visible": True, "defaultText": "Fasting sample"},
                "investigation_items": {"x": 10, "y": 40, "width": 80, "height": 80, "fontSize": 14, "lineHeight": 8, "visible": True},
            },
        )

        client = app.test_client()
        login(client, "doctor-investigation-custom-template@example.com")

        response = client.get(
            f"/print/investigations/{order.uuid}/preview?template_uuid={template.uuid}"
        )

        assert response.status_code == 200
        assert b"Custom Investigation Paper" in response.data
        assert b"Fasting sample" in response.data
        assert b"AMH" in response.data

        db.drop_all()


def test_unified_investigation_preview_redirects_when_order_has_no_items():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-investigation-empty@example.com", "01066440004", "Doctor")
        patient = create_patient(phone_primary="01066440104")
        visit = create_visit(patient)
        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)

        client = app.test_client()
        login(client, "doctor-investigation-empty@example.com")

        response = client.get(
            f"/print/investigations/{order.uuid}/preview",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Investigation order has no tests to print" in response.data

        db.drop_all()


def test_reception_cannot_open_unified_investigation_preview():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-investigation-print@example.com", "01066440005", "Reception")
        order = create_order_with_item()

        client = app.test_client()
        login(client, "reception-investigation-print@example.com")

        response = client.get(f"/print/investigations/{order.uuid}/preview")

        assert response.status_code == 403

        db.drop_all()


def test_investigation_order_detail_has_print_request_button():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-investigation-print-button@example.com", "01066440006", "Doctor")
        order = create_order_with_item()

        client = app.test_client()
        login(client, "doctor-investigation-print-button@example.com")

        response = client.get(f"/investigations/orders/{order.uuid}")

        assert response.status_code == 200
        assert b"Print request" in response.data
        assert b"/print/investigations/" in response.data

        db.drop_all()
