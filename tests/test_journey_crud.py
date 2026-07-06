from datetime import date

from app import create_app
from app.extensions import db
from app.models import Journey, User
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


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


def create_patient():
    return PatientService.create_patient(
        name_ar="سارة أحمد",
        name_en="Sara Ahmed",
        phone_primary="01000000000",
        date_of_birth=date(1996, 7, 1),
    )


def test_doctor_can_create_journey_from_patient():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01060000001", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/journeys/new",
                data={
                    "journey_type": "pregnancy",
                    "title": "Pregnancy 2026",
                    "description": "New pregnancy follow-up",
                    "start_date": "2026",
                },
                follow_redirects=True,
            )

        journey = Journey.query.filter_by(title="Pregnancy 2026").first()

        assert response.status_code == 200
        assert journey is not None
        assert journey.patient_id == patient.id
        assert b"Pregnancy 2026" in response.data

        db.drop_all()


def test_duplicate_active_journey_shows_error():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01060000002", "Doctor", "Doctor User")
        patient = create_patient()
        JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy 1",
            start_date="2026",
        )

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/journeys/new",
                data={
                    "journey_type": "pregnancy",
                    "title": "Pregnancy 2",
                    "description": "",
                    "start_date": "2027",
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert Journey.query.count() == 1
        assert b"already has an active pregnancy journey" in response.data

        db.drop_all()


def test_journey_detail_and_index_render():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01060000003", "Doctor", "Doctor User")
        patient = create_patient()
        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="gynecology",
            title="Bleeding follow-up",
            start_date="2026-07",
        )

        with app.test_client() as client:
            login(client, "doctor@example.com")
            detail = client.get(f"/journeys/{journey.uuid}")
            index = client.get(f"/patients/{patient.uuid}/journeys")

        assert detail.status_code == 200
        assert index.status_code == 200
        assert b"Bleeding follow-up" in detail.data
        assert b"Bleeding follow-up" in index.data

        db.drop_all()


def test_close_journey_route_accepts_year_only_end_date():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01060000004", "Doctor", "Doctor User")
        patient = create_patient()
        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="infertility",
            title="Infertility",
            start_date="2025",
        )

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.post(
                f"/journeys/{journey.uuid}/close",
                data={
                    "end_date": "2026",
                    "outcome": "lost_to_follow_up",
                    "outcome_note": "No follow-up.",
                    "confirm_close": "y",
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert journey.status == "closed"
        assert journey.end_date == date(2026, 1, 1)
        assert journey.end_date_precision == "year"
        assert b"Lost to follow-up" in response.data

        db.drop_all()


def test_reopen_journey_route_clears_outcome():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01060000005", "Doctor", "Doctor User")
        patient = create_patient()
        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="gynecology",
            title="Pain",
            start_date="2026",
        )
        JourneyService.close_journey(journey, outcome="resolved", end_date="2026")

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.post(
                f"/journeys/{journey.uuid}/reopen",
                data={
                    "confirm_reopen": "y",
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert journey.status == "active"
        assert journey.end_date is None
        assert journey.outcome is None

        db.drop_all()


def test_reception_cannot_create_journey():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01060000006", "Reception", "Reception User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/journeys/new",
                data={
                    "journey_type": "pregnancy",
                    "title": "Pregnancy",
                    "start_date": "2026",
                },
                follow_redirects=True,
            )

        assert response.status_code == 403
        assert Journey.query.count() == 0

        db.drop_all()
