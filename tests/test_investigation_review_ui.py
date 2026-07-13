from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.investigation import InvestigationResult, InvestigationTest
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_preset_service import InvestigationPresetService
from app.services.investigation_service import InvestigationService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.timeline_service import TimelineService
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
        "phone_primary": "01066930000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Investigation review UI visit",
    )


def create_test(code="review_ui_tsh", name="Review UI TSH"):
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


def test_doctor_can_open_pending_review_page():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-pending-review-ui@example.com", "01066930001", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        test = create_test()
        InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="2.0",
        )

        client = app.test_client()
        login(client, "doctor-pending-review-ui@example.com")

        response = client.get("/investigations/pending")

        assert response.status_code == 200
        assert b"Pending result review" in response.data
        assert b"Review UI TSH" in response.data

        db.drop_all()


def test_doctor_can_review_result_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-review-ui@example.com", "01066930002", "Doctor")
        patient = create_patient(phone_primary="01066930102")
        visit = create_visit(patient)
        test = create_test(code="review_submit_tsh", name="Review Submit TSH")

        result = InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="2.0",
            abnormal_flag=InvestigationResult.FLAG_UNKNOWN,
        )

        client = app.test_client()
        login(client, "doctor-review-ui@example.com")

        response = client.post(
            f"/investigations/results/{result.uuid}/review",
            data={
                "abnormal_flag": InvestigationResult.FLAG_NORMAL,
                "review_note": "Reviewed from UI",
            },
            follow_redirects=True,
        )

        db.session.refresh(result)

        assert response.status_code == 200
        assert b"Investigation result reviewed" in response.data
        assert result.status == InvestigationResult.STATUS_REVIEWED
        assert result.review_note == "Reviewed from UI"
        assert result.reviewed_at is not None

        db.drop_all()


def test_reception_cannot_review_results():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("reception-review-ui@example.com", "01066930003", "Reception")
        patient = create_patient(phone_primary="01066930103")
        visit = create_visit(patient)
        test = create_test(code="blocked_review", name="Blocked Review")

        result = InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="2.0",
        )

        client = app.test_client()
        login(client, "reception-review-ui@example.com")

        response = client.post(
            f"/investigations/results/{result.uuid}/review",
            data={
                "abnormal_flag": InvestigationResult.FLAG_NORMAL,
                "review_note": "Should fail",
            },
            follow_redirects=True,
        )

        assert response.status_code == 403

        db.drop_all()


def test_patient_workspace_shows_investigation_sections_and_missing_workup():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-workspace-investigation-ui@example.com", "01066930004", "Doctor")
        patient = create_patient(phone_primary="01066930104")
        visit = create_visit(patient)

        existing_test = create_test(code="workspace_existing_amh", name="Workspace Existing AMH")
        missing_test = create_test(code="workspace_missing_tsh", name="Workspace Missing TSH")
        preset = InvestigationPresetService.create_preset(name="Workspace Workup")
        InvestigationPresetService.add_item(preset=preset, test=existing_test)
        InvestigationPresetService.add_item(preset=preset, test=missing_test)

        InvestigationService.enter_historical_result(
            patient=patient,
            test=existing_test,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="1.5",
            lab_name="External Lab",
        )

        client = app.test_client()
        login(client, "doctor-workspace-investigation-ui@example.com")

        response = client.get(f"/patients/{patient.uuid}?preset_id={preset.id}")

        assert response.status_code == 200
        assert b"Investigation Workspace" in response.data
        assert b"Pending ordered results" in response.data
        assert b"Pending review" in response.data
        assert b"Latest results" in response.data
        assert b"Missing workup" in response.data
        assert b"Workspace Existing AMH" in response.data
        assert b"Workspace Missing TSH" in response.data
        assert b"External Lab" in response.data

        db.drop_all()


def test_timeline_includes_investigation_result_reviewed_event():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-timeline-investigation@example.com", "01066930005", "Doctor")
        patient = create_patient(phone_primary="01066930105")
        visit = create_visit(patient)
        test = create_test(code="timeline_review_tsh", name="Timeline Review TSH")

        result = InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="2.0",
        )
        InvestigationService.review_result(result, review_note="Timeline review", actor_user=doctor)

        events = TimelineService.get_patient_timeline(patient)

        assert any(event["type"] == "investigation_result_entered" for event in events)
        assert any(event["type"] == "investigation_result_reviewed" for event in events)
        assert any(event["title"] == "Timeline Review TSH" for event in events)

        db.drop_all()
