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


def test_booked_appointment_can_be_marked_arrived_from_route():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01040000001", "Reception", "Reception User")
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date(2026, 7, 7),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.post(
                f"/appointments/{appointment.uuid}/arrive",
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert appointment.status == Appointment.STATUS_ARRIVED
        assert appointment.arrived_at is not None
        assert patient.visits.count() == 0

        db.drop_all()


def test_arrived_appointment_appears_in_waiting_queue():
    app = make_app()

    with app.app_context():
        db.create_all()
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date(2026, 7, 7),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        AppointmentService.mark_arrived(appointment)

        queue = AppointmentService.get_waiting_queue(date(2026, 7, 7))

        assert appointment in queue

        db.drop_all()


def test_cancel_appointment_route_sets_cancelled_status():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01040000002", "Reception", "Reception User")
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date(2026, 7, 7),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.post(
                f"/appointments/{appointment.uuid}/cancel",
                data={"reason": "Patient called"},
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert appointment.status == Appointment.STATUS_CANCELLED
        assert appointment.cancelled_at is not None
        assert appointment.cancel_reason == "Patient called"

        db.drop_all()


def test_reschedule_appointment_route_creates_new_appointment():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01040000003", "Reception", "Reception User")
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date(2026, 7, 7),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.post(
                f"/appointments/{appointment.uuid}/reschedule",
                data={
                    "appointment_date": "2026-07-08",
                    "appointment_time": "10:30",
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert appointment.status == Appointment.STATUS_RESCHEDULED
        assert appointment.rescheduled_at is not None
        assert Appointment.query.count() == 2

        new_appointment = Appointment.query.filter(
            Appointment.id != appointment.id,
        ).first()

        assert new_appointment.appointment_date == date(2026, 7, 8)
        assert new_appointment.rescheduled_from_id == appointment.id

        db.drop_all()


def test_emergency_unscheduled_route_creates_arrived_emergency_without_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01040000004", "Reception", "Reception User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.post(
                "/appointments/emergency/new",
                data={
                    "patient_id": str(patient.id),
                    "appointment_date": "2026-07-07",
                    "appointment_time": "",
                    "duration_minutes": "",
                    "appointment_type": Appointment.TYPE_EMERGENCY,
                    "source": Appointment.SOURCE_EMERGENCY_UNSCHEDULED,
                    "notes": "Walk-in emergency",
                },
                follow_redirects=True,
            )

        appointment = Appointment.query.first()

        assert response.status_code == 200
        assert appointment is not None
        assert appointment.appointment_type == Appointment.TYPE_EMERGENCY
        assert appointment.source == Appointment.SOURCE_EMERGENCY_UNSCHEDULED
        assert appointment.status == Appointment.STATUS_ARRIVED
        assert appointment.appointment_time is not None
        assert appointment.appointment_time.second == 0
        assert appointment.appointment_time.microsecond == 0
        assert appointment.arrived_at is not None
        assert patient.visits.count() == 0

        db.drop_all()


def test_doctor_can_view_waiting_queue_service():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01040000005", "Doctor", "Doctor User")
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date(2026, 7, 7),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )
        AppointmentService.mark_arrived(appointment)

        queue = AppointmentService.get_waiting_queue(date(2026, 7, 7))

        assert len(queue) == 1
        assert queue[0].patient_id == patient.id

        db.drop_all()
