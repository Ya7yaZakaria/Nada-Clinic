from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
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


def create_patient(**overrides):
    data = {
        "name_ar": "سارة أحمد",
        "name_en": "Sara Ahmed",
        "phone_primary": "01000000000",
        "date_of_birth": date(1996, 7, 1),
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return PatientService.create_patient(**data)


def seed_calendar_data():
    patient = create_patient()
    arrived_patient = create_patient(phone_primary="01000000001")
    completed_patient = create_patient(phone_primary="01000000002")

    booked = AppointmentService.create_appointment(
        patient_id=arrived_patient.id,
        appointment_date=date(2026, 7, 7),
        appointment_type=Appointment.TYPE_NEW_CONSULTATION,
    )

    arrived = AppointmentService.create_appointment(
        patient_id=completed_patient.id,
        appointment_date=date(2026, 7, 7),
        appointment_type=Appointment.TYPE_FOLLOW_UP,
        source=Appointment.SOURCE_PHONE,
    )
    AppointmentService.mark_arrived(arrived)

    completed = AppointmentService.create_appointment(
        patient_id=patient.id,
        appointment_date=date(2026, 7, 7),
        appointment_type=Appointment.TYPE_EMERGENCY,
        source=Appointment.SOURCE_WHATSAPP,
    )
    AppointmentService.mark_no_show(completed)

    return patient, booked, arrived, completed


def test_doctor_can_view_calendar():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01030000001", "Doctor", "Doctor User")
        seed_calendar_data()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/appointments/calendar?date=2026-07-07&view=month")

        assert response.status_code == 200
        assert b"Appointment Calendar" in response.data
        assert b"Sara Ahmed" in response.data

        db.drop_all()


def test_calendar_month_week_day_render():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01030000002", "Doctor", "Doctor User")
        seed_calendar_data()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            month_response = client.get("/appointments/calendar?date=2026-07-07&view=month")
            week_response = client.get("/appointments/calendar?date=2026-07-07&view=week")
            day_response = client.get("/appointments/calendar?date=2026-07-07&view=day")

        assert month_response.status_code == 200
        assert week_response.status_code == 200
        assert day_response.status_code == 200
        assert b"Week view" in week_response.data
        assert b"Day view" in day_response.data

        db.drop_all()


def test_calendar_shows_count_and_includes_changed_statuses():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01030000003", "Doctor", "Doctor User")
        seed_calendar_data()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/appointments/calendar?date=2026-07-07&view=month")

        assert response.status_code == 200
        assert b">3</span>" in response.data
        assert b"Booked" in response.data
        assert b"Waiting" in response.data
        assert b"No-show" in response.data

        db.drop_all()


def test_selected_day_appointments_render_type_and_status():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01030000004", "Doctor", "Doctor User")
        seed_calendar_data()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/appointments/calendar?date=2026-07-07&view=day")

        assert response.status_code == 200
        assert b"New Consultation" in response.data
        assert b"Follow-up" in response.data
        assert b"Emergency" in response.data
        assert b"Booked" in response.data
        assert b"Waiting" in response.data
        assert b"No-show" in response.data

        db.drop_all()


def test_calendar_does_not_create_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01030000005", "Doctor", "Doctor User")
        patient, _, _, _ = seed_calendar_data()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/appointments/calendar?date=2026-07-07&view=day")

        assert response.status_code == 200
        assert patient.visits.count() == 0

        db.drop_all()
