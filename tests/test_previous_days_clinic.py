from datetime import date, timedelta

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


def create_user(email="doctor@example.com", role_name="Doctor"):
    user = User(email=email, phone="01055550000", name="Previous Days Tester")
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)

    return user


def login(client, email="doctor@example.com"):
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
        name_ar="منى علي",
        name_en="Mona Ali",
        phone_primary="01011112222",
        date_of_birth=date(1990, 1, 1),
        governorate="Qalyubia",
        city="Benha",
        street="Main Street",
    )


def test_previous_days_page_renders():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user()
        patient = create_patient()

        past_date = date.today() - timedelta(days=1)
        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        with app.test_client() as client:
            login(client)
            response = client.get("/clinic/previous")

        assert response.status_code == 200
        assert b"Previous Clinic Days" in response.data
        assert past_date.isoformat().encode() in response.data

        db.drop_all()


def test_previous_days_only_show_past_dates():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user()
        patient = create_patient()

        past_date = date.today() - timedelta(days=2)
        today = date.today()

        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=today,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        with app.test_client() as client:
            login(client)
            response = client.get("/clinic/previous")

        assert response.status_code == 200
        assert past_date.isoformat().encode() in response.data
        assert today.isoformat().encode() not in response.data

        db.drop_all()


def test_day_summary_counters_work():
    app = make_app()

    with app.app_context():
        db.create_all()
        patient = create_patient()
        past_date = date.today() - timedelta(days=1)

        booked = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        arrived = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_arrived(arrived)

        completed = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_completed(completed)

        no_show = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_no_show(no_show)

        summary = AppointmentService.get_day_summary(past_date)

        assert summary["counters"]["total_booked_today"] == 4
        assert summary["counters"]["booked"] == 1
        assert summary["counters"]["arrived"] == 1
        assert summary["counters"]["completed"] == 1
        assert summary["counters"]["no_show"] == 1
        assert len(summary["unfinished"]) == 2
        assert booked in summary["unfinished"]
        assert arrived in summary["unfinished"]

        db.drop_all()


def test_unfinished_arrived_appointment_appears_in_past_day():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user()
        patient = create_patient()
        past_date = date.today() - timedelta(days=1)

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )
        AppointmentService.mark_arrived(appointment)

        with app.test_client() as client:
            login(client)
            response = client.get(f"/clinic/day/{past_date.isoformat()}")

        assert response.status_code == 200
        assert b"Arrived but not completed" in response.data
        assert b"Mona Ali" in response.data
        assert b"Waiting" in response.data

        db.drop_all()


def test_no_show_completed_cancelled_rescheduled_appear_in_past_day():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user()
        patient = create_patient()
        past_date = date.today() - timedelta(days=1)

        no_show = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_no_show(no_show)

        completed = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_completed(completed)

        cancelled = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.cancel_appointment(cancelled)

        rescheduled = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.reschedule_appointment(
            rescheduled,
            new_date=date.today() + timedelta(days=1),
        )

        with app.test_client() as client:
            login(client)
            response = client.get(f"/clinic/day/{past_date.isoformat()}")

        assert response.status_code == 200
        assert b"No-show" in response.data
        assert b"Completed" in response.data
        assert b"Cancelled" in response.data
        assert b"Rescheduled" in response.data
        assert b"Cancelled / Rescheduled" in response.data

        db.drop_all()


def test_previous_day_navigation_link_works():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user()
        patient = create_patient()
        past_date = date.today() - timedelta(days=3)

        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=past_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        with app.test_client() as client:
            login(client)
            previous_response = client.get("/clinic/previous")
            day_response = client.get(f"/clinic/day/{past_date.isoformat()}")

        assert previous_response.status_code == 200
        assert f"/clinic/day/{past_date.isoformat()}".encode() in previous_response.data
        assert day_response.status_code == 200
        assert b"Clinic Day Summary" in day_response.data

        db.drop_all()


def test_previous_days_uses_generated_view_no_table():
    app = make_app()

    with app.app_context():
        db.create_all()

        tables = set(db.metadata.tables.keys())

        assert "clinic_days" not in tables
        assert "today_clinic" not in tables
        assert "previous_clinic_days" not in tables

        db.drop_all()
