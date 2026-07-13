from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.investigation import InvestigationOrderItem, InvestigationResult, InvestigationTest
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_service import InvestigationService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost", WTF_CSRF_ENABLED=False)
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
    return client.post("/auth/login", data={"login_identifier": email, "password": "12345678"}, follow_redirects=True)


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01066730000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient):
    return VisitService.create_visit(patient=patient, visit_type="gyn", chief_complaint="Result UI visit")


def create_test(code="tsh", name="TSH"):
    category = InvestigationDictionaryService.create_category(code=f"{code}_category", name_en=f"{name} Category")
    return InvestigationDictionaryService.create_test(
        code=code,
        name_en=name,
        category=category,
        default_unit="mIU/L",
        default_reference_range="0.4-4.0",
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def test_doctor_can_open_ordered_result_entry_page():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-result-entry-page@example.com", "01066730001", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        test = create_test()
        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        item = InvestigationService.add_order_item(order=order, test=test)

        client = app.test_client()
        login(client, "doctor-result-entry-page@example.com")
        response = client.get(f"/investigations/items/{item.uuid}/result/new")

        assert response.status_code == 200
        assert b"Enter Investigation Result" in response.data
        assert b"TSH" in response.data
        db.drop_all()


def test_doctor_can_enter_ordered_result_from_ui():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-save-ordered-result@example.com", "01066730002", "Doctor")
        patient = create_patient(phone_primary="01066730102")
        visit = create_visit(patient)
        test = create_test(code="ordered_ui_tsh", name="Ordered UI TSH")
        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        item = InvestigationService.add_order_item(order=order, test=test)

        client = app.test_client()
        login(client, "doctor-save-ordered-result@example.com")
        response = client.post(
            f"/investigations/items/{item.uuid}/result/new",
            data={
                "result_date": "2026-07-13",
                "lab_name": "Al Borg",
                "result_value": "2.1",
                "unit": "mIU/L",
                "reference_range": "0.4-4.0",
                "doctor_comment": "Acceptable",
                "abnormal_flag": InvestigationResult.FLAG_NORMAL,
            },
            follow_redirects=True,
        )

        result = InvestigationResult.query.filter_by(order_item_id=item.id).first()

        assert response.status_code == 200
        assert b"Investigation result entered" in response.data
        assert result is not None
        assert result.result_value == "2.1"
        assert result.lab_name == "Al Borg"
        assert result.doctor_comment == "Acceptable"
        db.session.refresh(item)
        assert item.status == InvestigationOrderItem.STATUS_RESULT_ENTERED
        db.drop_all()


def test_doctor_can_enter_historical_result_from_patient_ui():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-historical-patient-ui@example.com", "01066730003", "Doctor")
        patient = create_patient(phone_primary="01066730103")
        test = create_test(code="historical_patient_amh", name="Historical Patient AMH")

        client = app.test_client()
        login(client, "doctor-historical-patient-ui@example.com")
        response = client.post(
            f"/investigations/patients/{patient.uuid}/results/new",
            data={
                "test_id": str(test.id),
                "result_date": "2026-07-13",
                "lab_name": "Al Mokhtabar",
                "result_value": "1.2",
                "unit": "ng/mL",
                "abnormal_flag": InvestigationResult.FLAG_NORMAL,
            },
            follow_redirects=True,
        )

        result = InvestigationResult.query.filter_by(patient_id=patient.id, test_id=test.id).first()

        assert response.status_code == 200
        assert b"Historical investigation result entered" in response.data
        assert result is not None
        assert result.order_item_id is None
        assert result.result_value == "1.2"
        db.drop_all()


def test_doctor_can_enter_historical_result_from_visit_ui():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-historical-visit-ui@example.com", "01066730004", "Doctor")
        patient = create_patient(phone_primary="01066730104")
        visit = create_visit(patient)
        test = create_test(code="historical_visit_tsh", name="Historical Visit TSH")

        client = app.test_client()
        login(client, "doctor-historical-visit-ui@example.com")
        response = client.post(
            f"/investigations/visits/{visit.uuid}/results/new",
            data={
                "test_id": str(test.id),
                "result_date": "2026-07-13",
                "lab_name": "External Lab",
                "result_value": "3.0",
                "abnormal_flag": InvestigationResult.FLAG_NORMAL,
            },
            follow_redirects=True,
        )

        result = InvestigationResult.query.filter_by(patient_id=patient.id, test_id=test.id).first()

        assert response.status_code == 200
        assert b"Historical investigation result entered" in response.data
        assert result is not None
        assert result.result_visit == visit
        db.drop_all()


def test_patient_investigations_page_shows_historical_button_and_result():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-patient-results-page@example.com", "01066730005", "Doctor")
        patient = create_patient(phone_primary="01066730105")
        visit = create_visit(patient)
        test = create_test(code="patient_page_result", name="Patient Page Result")
        InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            lab_name="External Lab",
            result_value="5.0",
        )

        client = app.test_client()
        login(client, "doctor-patient-results-page@example.com")
        response = client.get(f"/investigations/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"Add historical result" in response.data
        assert b"Patient Page Result" in response.data
        assert b"External Lab" in response.data
        db.drop_all()


def test_reception_cannot_enter_investigation_result():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-result-entry@example.com", "01066730006", "Reception")
        patient = create_patient(phone_primary="01066730106")
        visit = create_visit(patient)
        test = create_test(code="blocked_result", name="Blocked Result")
        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        item = InvestigationService.add_order_item(order=order, test=test)

        client = app.test_client()
        login(client, "reception-result-entry@example.com")
        response = client.get(f"/investigations/items/{item.uuid}/result/new")

        assert response.status_code == 403
        db.drop_all()
