from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.investigation import InvestigationOrder, InvestigationOrderItem, InvestigationTest
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_service import InvestigationService
from app.services.patient_service import PatientService
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
        "phone_primary": "01066330000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Investigation visit",
    )


def create_investigation_test(code="tsh", name="TSH"):
    category = InvestigationDictionaryService.create_category(
        code=f"{code}_category",
        name_en=f"{name} Category",
    )
    return InvestigationDictionaryService.create_test(
        code=code,
        name_en=name,
        category=category,
        default_unit="mIU/L",
        default_reference_range="0.4-4.0",
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def test_doctor_sees_investigations_section_in_visit_detail():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-investigation-ui@example.com", "01066330001", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        create_investigation_test()

        client = app.test_client()
        login(client, "doctor-investigation-ui@example.com")

        response = client.get(f"/visits/{visit.uuid}")

        assert response.status_code == 200
        assert b"Investigation orders" in response.data
        assert b"New order" in response.data
        assert b"Patient investigations" in response.data

        db.drop_all()


def test_doctor_can_create_investigation_order_from_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-create-investigation-order@example.com", "01066330002", "Doctor")
        patient = create_patient(phone_primary="01066330102")
        visit = create_visit(patient)

        client = app.test_client()
        login(client, "doctor-create-investigation-order@example.com")

        response = client.post(
            f"/investigations/visits/{visit.uuid}/new",
            data={
                "priority": InvestigationOrder.PRIORITY_IMPORTANT,
                "order_notes": "Initial infertility workup",
            },
            follow_redirects=True,
        )

        order = InvestigationOrder.query.filter_by(ordered_visit_id=visit.id).first()

        assert response.status_code == 200
        assert b"Investigation order created" in response.data
        assert order is not None
        assert order.patient == patient
        assert order.priority == InvestigationOrder.PRIORITY_IMPORTANT
        assert order.order_notes == "Initial infertility workup"

        db.drop_all()


def test_doctor_can_add_test_to_investigation_order():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-add-investigation-item@example.com", "01066330003", "Doctor")
        patient = create_patient(phone_primary="01066330103")
        visit = create_visit(patient)
        test = create_investigation_test()

        order = InvestigationService.create_order(
            patient=patient,
            ordered_visit=visit,
        )

        client = app.test_client()
        login(client, "doctor-add-investigation-item@example.com")

        response = client.post(
            f"/investigations/orders/{order.uuid}/items",
            data={
                "test_id": str(test.id),
                "item_notes": "Morning sample",
            },
            follow_redirects=True,
        )

        item = InvestigationOrderItem.query.filter_by(order_id=order.id).first()

        assert response.status_code == 200
        assert b"Investigation test added" in response.data
        assert item is not None
        assert item.test == test
        assert item.item_notes == "Morning sample"
        assert item.status == InvestigationOrderItem.STATUS_PENDING_RESULT

        db.drop_all()


def test_visit_detail_shows_order_and_pending_item():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-view-investigation-order@example.com", "01066330004", "Doctor")
        patient = create_patient(phone_primary="01066330104")
        visit = create_visit(patient)
        test = create_investigation_test(code="amh", name="AMH")

        order = InvestigationService.create_order(
            patient=patient,
            ordered_visit=visit,
        )
        InvestigationService.add_order_item(order=order, test=test)

        client = app.test_client()
        login(client, "doctor-view-investigation-order@example.com")

        response = client.get(f"/visits/{visit.uuid}")

        assert response.status_code == 200
        assert b"Orders: 1" in response.data
        assert b"Pending: 1" in response.data
        assert b"AMH" in response.data

        db.drop_all()


def test_reception_cannot_create_investigation_order_from_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-investigation-ui@example.com", "01066330005", "Reception")
        patient = create_patient(phone_primary="01066330105")
        visit = create_visit(patient)

        client = app.test_client()
        login(client, "reception-investigation-ui@example.com")

        response = client.get(f"/investigations/visits/{visit.uuid}/new")

        assert response.status_code == 403

        db.drop_all()


def test_doctor_can_open_patient_investigations_page():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-patient-investigations@example.com", "01066330006", "Doctor")
        patient = create_patient(phone_primary="01066330106")
        visit = create_visit(patient)
        test = create_investigation_test(code="prl", name="Prolactin")
        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        InvestigationService.add_order_item(order=order, test=test)

        client = app.test_client()
        login(client, "doctor-patient-investigations@example.com")

        response = client.get(f"/investigations/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"Pending results" in response.data
        assert b"Latest results" in response.data
        assert b"Prolactin" in response.data

        db.drop_all()


def test_investigations_sidebar_link_is_active_for_doctor():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-investigation-sidebar@example.com", "01066330007", "Doctor")

        client = app.test_client()
        login(client, "doctor-investigation-sidebar@example.com")

        response = client.get("/")

        assert response.status_code == 200
        assert b"/investigations/" in response.data
        assert b"Stage 6 Investigations" in response.data

        db.drop_all()
