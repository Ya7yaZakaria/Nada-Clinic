from datetime import date

from app import create_app
from datetime import timedelta
from app.extensions import db
from app.models import Appointment, Patient, User, Visit
from app.services.appointment_service import (
    AppointmentService,
)
from app.services.clinic_day_service import (
    ClinicDayService,
)
from app.services.rbac_service import RBACService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
    )
    return app


def create_user(role, email, phone):
    user = User(
        email=email,
        phone=phone,
        name=f"{role} User",
    )
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role)
    return user


def create_patient(number=88001):
    patient = Patient(
        medical_file_number=number,
        name_ar="Test Patient",
        name_en="Test Patient",
        search_name="test patient",
        gender="female",
        phone_primary=f"010{number}",
    )
    db.session.add(patient)
    db.session.commit()
    return patient


def login(client, email):
    return client.post(
        "/auth/login",
        data={
            "login_identifier": email,
            "password": "12345678",
        },
    )


def test_undo_arrived_returns_booking_to_booked():
    app = make_app()

    with app.app_context():
        db.create_all()
        patient = create_patient()

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        AppointmentService.mark_arrived(
            appointment
        )
        AppointmentService.undo_arrived(
            appointment
        )

        assert (
            appointment.status
            == Appointment.STATUS_BOOKED
        )
        assert appointment.arrived_at is None

        db.drop_all()


def test_close_day_converts_booked_and_keeps_arrived():
    app = make_app()

    with app.app_context():
        db.create_all()
        patient = create_patient()
        arrived_patient = create_patient(88002)

        booked = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_NEW_CONSULTATION
                ),
            )
        )

        arrived = (
            AppointmentService.create_appointment(
                patient_id=arrived_patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        AppointmentService.mark_arrived(
            arrived
        )

        converted = (
            AppointmentService.close_clinic_day(
                date.today()
            )
        )

        assert booked in converted
        assert (
            booked.status
            == Appointment.STATUS_NO_SHOW
        )
        assert booked.no_show_at is not None
        assert (
            arrived.status
            == Appointment.STATUS_ARRIVED
        )

        db.drop_all()


def test_visit_completion_drives_clinic_counter():
    app = make_app()

    with app.app_context():
        db.create_all()
        patient = create_patient()

        db.session.add(
            Visit(
                patient_id=patient.id,
                visit_type="gyn",
                status="completed",
            )
        )
        db.session.commit()

        snapshot = (
            ClinicDayService.get_visit_snapshot(
                date.today()
            )
        )

        assert snapshot["total"] == 1
        assert snapshot["completed"] == 1
        assert (
            snapshot["by_patient"][patient.id]
            .status
            == "completed"
        )

        db.drop_all()


def test_live_counters_match_visible_operational_lists():
    app = make_app()

    with app.app_context():
        db.create_all()
        waiting_patient = create_patient(88101)
        open_patient = create_patient(88102)
        completed_patient = create_patient(88103)
        booked_patient = create_patient(88104)

        waiting = AppointmentService.create_appointment(
            patient_id=waiting_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_arrived(waiting)

        open_appointment = AppointmentService.create_appointment(
            patient_id=open_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        VisitService.create_visit(
            patient=open_patient,
            appointment=open_appointment,
            visit_type="general",
        )

        completed_appointment = AppointmentService.create_appointment(
            patient_id=completed_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        completed_visit = VisitService.create_visit(
            patient=completed_patient,
            appointment=completed_appointment,
            visit_type="general",
        )
        VisitService.complete_visit(completed_visit, confirmed=True)

        booked = AppointmentService.create_appointment(
            patient_id=booked_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        clinic_day = AppointmentService.get_clinic_day(date.today())
        counters = ClinicDayService.build_live_counters(
            clinic_day,
            ClinicDayService.get_visit_snapshot(date.today()),
        )

        assert clinic_day["waiting_queue"] == [waiting]
        assert clinic_day["booked_no_action"] == [booked]
        assert counters["waiting"] == 1
        assert counters["remaining"] == 2

        db.drop_all()


def test_today_clinic_uses_booking_and_visit_actions():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "today-live-reception@example.com",
            "01088000002",
        )
        patient = create_patient()

        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=(
                Appointment.TYPE_NEW_CONSULTATION
            ),
        )

        client = app.test_client()

        login(
            client,
            "today-live-reception@example.com",
        )

        response = client.get(
            f"/clinic/day/{date.today().isoformat()}"
        )

        assert response.status_code == 200
        assert b"Waiting Now" in response.data
        assert b"Visits Completed" in response.data
        assert b"Mark Arrived" in response.data
        assert b"Manage Booking" in response.data

        assert b"Still Booked" not in response.data
        assert b"Mark Completed" not in response.data
        assert b"Completed Appointments" not in response.data

        db.drop_all()


def test_resolved_controls_and_linked_visit_actions_render():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user(
            "Doctor",
            "today-resolved-doctor@example.com",
            "01088000003",
        )
        completed_patient = create_patient(88201)
        cancelled_patient = create_patient(88202)
        rescheduled_patient = create_patient(88203)

        completed_appointment = AppointmentService.create_appointment(
            patient_id=completed_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        completed_visit = VisitService.create_visit(
            patient=completed_patient,
            appointment=completed_appointment,
            visit_type="general",
        )
        VisitService.complete_visit(completed_visit, confirmed=True)

        cancelled = AppointmentService.create_appointment(
            patient_id=cancelled_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.cancel_appointment(
            cancelled,
            reason="Patient unavailable",
        )

        rescheduled = AppointmentService.create_appointment(
            patient_id=rescheduled_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        destination = AppointmentService.reschedule_appointment(
            rescheduled,
            new_date=date.today() + timedelta(days=1),
        )

        client = app.test_client()
        login(client, "today-resolved-doctor@example.com")
        response = client.get(
            f"/clinic/day/{date.today().isoformat()}?resolved_filter=all&resolved_sort=latest"
        )

        assert response.status_code == 200
        assert b"resolved_filter" in response.data
        assert b"resolved_sort" in response.data
        assert b"Visit Completed" in response.data
        assert b"Resolved" in response.data
        assert b"Patient unavailable" in response.data
        assert b"Moved to" in response.data
        assert str(destination.appointment_date).encode() in response.data
        assert b"Open Visit" in response.data
        assert b"Undo Arrived" not in response.data

        db.drop_all()


def test_resolved_controls_remain_visible_for_empty_filter():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user(
            "Doctor",
            "today-empty-resolved@example.com",
            "01088000004",
        )
        client = app.test_client()
        login(client, "today-empty-resolved@example.com")
        response = client.get(
            f"/clinic/day/{date.today().isoformat()}?resolved_filter=completed"
        )

        assert response.status_code == 200
        assert b"resolved_filter" in response.data
        assert b"Latest resolved" in response.data
        assert b"No resolved bookings match this filter." in response.data

        db.drop_all()
