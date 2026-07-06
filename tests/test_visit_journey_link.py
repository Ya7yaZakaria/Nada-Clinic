from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Journey, User, Visit
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
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


def create_journey(patient, journey_type="pregnancy", title="Pregnancy 2026"):
    return JourneyService.create_journey(
        patient=patient,
        journey_type=journey_type,
        title=title,
        start_date="2026",
    )


def test_visit_can_exist_without_journey():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        visit = VisitService.create_visit(patient=patient, visit_type="general")

        assert visit.journey_id is None
        assert VisitService.has_unassigned_warning(visit) is True

        db.drop_all()


def test_visit_can_be_created_with_journey():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        journey = create_journey(patient)

        visit = VisitService.create_visit(
            patient=patient,
            journey_id=journey.id,
            visit_type="obs",
        )

        assert visit.journey_id == journey.id
        assert visit.journey == journey
        assert VisitService.has_unassigned_warning(visit) is False

        db.drop_all()


def test_assign_journey_later():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        journey = create_journey(patient)
        visit = VisitService.create_visit(patient=patient, visit_type="general")

        VisitService.assign_journey(visit, journey.id)

        assert visit.journey_id == journey.id

        db.drop_all()


def test_remove_journey_link():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        journey = create_journey(patient)
        visit = VisitService.create_visit(patient=patient, journey_id=journey.id, visit_type="general")

        VisitService.remove_journey(visit)

        assert visit.journey_id is None
        assert VisitService.has_unassigned_warning(visit) is True

        db.drop_all()


def test_cannot_assign_other_patient_journey():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        first_patient = create_patient(phone_primary="01000000001")
        second_patient = create_patient(
            name_ar="منى أحمد",
            name_en="Mona Ahmed",
            phone_primary="01000000002",
        )
        other_journey = create_journey(second_patient)
        visit = VisitService.create_visit(patient=first_patient, visit_type="general")

        with pytest.raises(ValueError, match="Journey belongs to another patient"):
            VisitService.assign_journey(visit, other_journey.id)

        db.drop_all()


def test_closed_journey_can_be_assigned():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        journey = create_journey(patient)
        JourneyService.close_journey(journey, outcome="delivered", end_date="2026")

        visit = VisitService.create_visit(
            patient=patient,
            journey_id=journey.id,
            visit_type="obs",
        )

        assert journey.status == "closed"
        assert visit.journey_id == journey.id

        db.drop_all()


def test_doctor_can_create_visit_with_journey_route():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01070000001", "Doctor", "Doctor User")
        patient = create_patient()
        journey = create_journey(patient)

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/visits/new",
                data={
                    "visit_type": "obs",
                    "journey_id": str(journey.id),
                    "chief_complaint": "ANC visit",
                    "history": "",
                    "examination": "",
                    "assessment": "",
                    "plan": "",
                    "follow_up_date": "",
                },
                follow_redirects=True,
            )

        visit = Visit.query.first()

        assert response.status_code == 200
        assert visit is not None
        assert visit.journey_id == journey.id
        assert b"Pregnancy 2026" in response.data

        db.drop_all()


def test_create_visit_without_journey_route_shows_warning():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01070000002", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/visits/new",
                data={
                    "visit_type": "general",
                    "journey_id": "",
                    "chief_complaint": "General complaint",
                    "history": "",
                    "examination": "",
                    "assessment": "",
                    "plan": "",
                    "follow_up_date": "",
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert b"not linked to any Journey" in response.data

        db.drop_all()


def test_workspace_shows_active_journeys_and_recent_visits():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01070000003", "Doctor", "Doctor User")
        patient = create_patient()
        journey = create_journey(patient)
        VisitService.create_visit(patient=patient, journey_id=journey.id, visit_type="obs")

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"Active Journeys" in response.data
        assert b"Pregnancy 2026" in response.data
        assert b"Recent Visits" in response.data

        db.drop_all()


def test_reception_cannot_create_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01070000004", "Reception", "Reception User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/visits/new",
                data={
                    "visit_type": "general",
                    "journey_id": "",
                },
                follow_redirects=True,
            )

        assert response.status_code == 403
        assert Visit.query.count() == 0

        db.drop_all()
