from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.timeline_service import TimelineService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
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
        "name_ar": "سارة أحمد",
        "name_en": "Sara Ahmed",
        "phone_primary": "01000000000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def test_timeline_empty_patient_has_no_events():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        events = TimelineService.get_patient_timeline(patient)

        assert events == []

        db.drop_all()


def test_timeline_includes_journey_started_event():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy 2026",
            start_date="2026",
        )

        events = TimelineService.get_patient_timeline(patient)

        assert any(event["type"] == "journey_started" for event in events)
        assert any(event["source_uuid"] == journey.uuid for event in events)

        db.drop_all()


def test_timeline_includes_journey_closed_event():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy 2026",
            start_date="2026",
        )
        JourneyService.close_journey(
            journey,
            outcome="delivered",
            end_date="2026",
        )

        events = TimelineService.get_patient_timeline(patient)

        assert any(event["type"] == "journey_closed" for event in events)
        assert any(event["subtitle"] == "delivered" for event in events)

        db.drop_all()


def test_timeline_includes_visit_event():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = VisitService.create_visit(
            patient=patient,
            visit_type="gyn",
            chief_complaint="Pain",
        )

        events = TimelineService.get_patient_timeline(patient)

        assert any(event["type"] == "visit" for event in events)
        assert any(event["source_uuid"] == visit.uuid for event in events)

        db.drop_all()


def test_timeline_marks_unassigned_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        VisitService.create_visit(patient=patient, visit_type="general")

        events = TimelineService.get_patient_timeline(patient)
        visit_event = next(event for event in events if event["type"] == "visit")

        assert visit_event["is_unassigned"] is True

        db.drop_all()


def test_timeline_includes_completed_visit_event():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        doctor = create_user("doctor@example.com", "01080000001", "Doctor", "Doctor User")
        visit = VisitService.create_visit(patient=patient, visit_type="general")

        VisitService.complete_visit(visit, actor_user=doctor, confirmed=True)

        events = TimelineService.get_patient_timeline(patient)

        assert any(event["type"] == "visit_completed" for event in events)

        db.drop_all()


def test_timeline_includes_reopened_visit_event():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        doctor = create_user("doctor@example.com", "01080000002", "Doctor", "Doctor User")
        visit = VisitService.create_visit(patient=patient, visit_type="general")

        VisitService.complete_visit(visit, actor_user=doctor, confirmed=True)
        VisitService.reopen_visit(visit, actor_user=doctor, confirmed=True)

        events = TimelineService.get_patient_timeline(patient)

        assert any(event["type"] == "visit_reopened" for event in events)

        db.drop_all()


def test_timeline_is_sorted_newest_first():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        JourneyService.create_journey(
            patient=patient,
            journey_type="gynecology",
            title="Old journey",
            start_date="2024",
        )
        VisitService.create_visit(patient=patient, visit_type="general")

        events = TimelineService.get_patient_timeline(patient)
        dates = [event["date"] for event in events]

        assert dates == sorted(dates, reverse=True)

        db.drop_all()


def test_patient_workspace_shows_timeline_section():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01080000003", "Doctor", "Doctor User")
        patient = create_patient()
        JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy 2026",
            start_date="2026",
        )

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"Timeline" in response.data
        assert b"Journey started" in response.data
        assert b"Pregnancy 2026" in response.data

        db.drop_all()


def test_no_timeline_table_exists():
    from app import models

    assert not hasattr(models, "Timeline")
