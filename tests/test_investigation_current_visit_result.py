from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.investigation import InvestigationResult, InvestigationTest
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
        "phone_primary": "01066660000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_investigation_test():
    category = InvestigationDictionaryService.create_category(
        code="hormonal_current_visit",
        name_en="Hormonal",
    )
    return InvestigationDictionaryService.create_test(
        code="amh_current_visit",
        name_en="AMH",
        category=category,
        default_unit="ng/mL",
        default_reference_range="0.4-4.0",
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def setup_ordered_pending_item():
    patient = create_patient()
    ordered_visit = VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Order labs",
    )
    result_visit = VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Review results",
    )

    test = create_investigation_test()
    order = InvestigationService.create_order(
        patient=patient,
        ordered_visit=ordered_visit,
    )
    item = InvestigationService.add_order_item(order=order, test=test)

    return patient, ordered_visit, result_visit, order, item


def test_enter_ordered_result_from_current_visit_links_result_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-current-result@example.com", "01066660001", "Doctor")
        patient, ordered_visit, result_visit, order, item = setup_ordered_pending_item()

        client = app.test_client()
        login(client, "doctor-current-result@example.com")

        response = client.post(
            f"/investigations/visits/{result_visit.uuid}/items/{item.uuid}/result/new",
            data={
                "result_date": "2026-07-13",
                "lab_name": "External Lab",
                "result_value": "2.1",
                "unit": "ng/mL",
                "reference_range": "0.4-4.0",
                "result_text": "",
                "doctor_comment": "Reviewed during current visit",
                "abnormal_flag": InvestigationResult.FLAG_NORMAL,
                "has_attachment": "",
                "attachment_label": "",
                "external_report_reference": "",
            },
            follow_redirects=True,
        )

        saved_result = InvestigationResult.query.filter_by(order_item_id=item.id).first()

        assert response.status_code == 200
        assert b"Investigation result entered for current visit" in response.data
        assert saved_result is not None
        assert saved_result.ordered_visit_id == ordered_visit.id
        assert saved_result.result_visit_id == result_visit.id
        assert saved_result.result_visit_id != saved_result.ordered_visit_id

        db.drop_all()


def test_visit_detail_shows_previous_pending_result_action():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-current-result-button@example.com", "01066660002", "Doctor")
        patient, ordered_visit, result_visit, order, item = setup_ordered_pending_item()

        client = app.test_client()
        login(client, "doctor-current-result-button@example.com")

        response = client.get(f"/visits/{result_visit.uuid}")

        assert response.status_code == 200
        assert b"Pending results from previous visits" in response.data
        assert b"Enter result in this visit" in response.data
        assert f"/investigations/visits/{result_visit.uuid}/items/{item.uuid}/result/new".encode("utf-8") in response.data

        db.drop_all()


def test_current_visit_result_route_blocks_other_patient_item():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-current-result-block@example.com", "01066660003", "Doctor")
        patient, ordered_visit, result_visit, order, item = setup_ordered_pending_item()

        other_patient = create_patient(phone_primary="01066660103")
        other_visit = VisitService.create_visit(
            patient=other_patient,
            visit_type="gyn",
            chief_complaint="Other patient visit",
        )

        client = app.test_client()
        login(client, "doctor-current-result-block@example.com")

        response = client.get(
            f"/investigations/visits/{other_visit.uuid}/items/{item.uuid}/result/new",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Investigation item does not belong to this visit patient" in response.data

        db.drop_all()
