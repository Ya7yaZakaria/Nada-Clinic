from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models import User
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
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
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return PatientService.create_patient(**data)


def test_today_clinic_requires_login():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.get("/clinic/today")

        assert response.status_code in {302, 401}

        db.drop_all()


def test_doctor_can_view_today_clinic():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01044000001", "Doctor", "Doctor User")
        patient = create_patient()
        arrived_patient = create_patient(phone_primary="01000000011")
        cancelled_patient = create_patient(phone_primary="01000000012")
        rescheduled_patient = create_patient(phone_primary="01000000013")
        AppointmentService.create_appointment(
            patient_id=arrived_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/clinic/today", follow_redirects=True)

        assert response.status_code == 200
        assert b"Today" in response.data
        assert b"Sara Ahmed" in response.data

        db.drop_all()


def test_reception_can_view_today_clinic():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01044000002", "Reception", "Reception User")
        patient = create_patient()
        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.get("/clinic/today", follow_redirects=True)

        assert response.status_code == 200
        assert b"Sara Ahmed" in response.data

        db.drop_all()


def test_today_clinic_counters_include_all_statuses_and_emergency():
    app = make_app()

    with app.app_context():
        db.create_all()
        patient = create_patient()
        arrived_patient = create_patient(phone_primary="01000000011")
        cancelled_patient = create_patient(phone_primary="01000000012")
        rescheduled_patient = create_patient(phone_primary="01000000013")
        clinic_date = date.today()

        booked = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        arrived = AppointmentService.create_appointment(
            patient_id=arrived_patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_arrived(arrived)

        cancelled = AppointmentService.create_appointment(
            patient_id=cancelled_patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.cancel_appointment(cancelled)

        rescheduled = AppointmentService.create_appointment(
            patient_id=rescheduled_patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.reschedule_appointment(
            rescheduled,
            new_date=clinic_date + timedelta(days=1),
        )

        emergency = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_EMERGENCY,
            status=Appointment.STATUS_NO_SHOW,
            source=Appointment.SOURCE_EMERGENCY_UNSCHEDULED,
        )

        counters = AppointmentService.get_counters_for_date(clinic_date)

        assert counters["total_booked_today"] == 5
        assert counters["booked"] == 1
        assert counters["arrived"] == 1
        assert counters["cancelled"] == 1
        assert counters["rescheduled"] == 1
        assert counters["no_show"] == 1
        assert counters["emergency"] == 1
        assert booked.status == Appointment.STATUS_BOOKED
        assert emergency.source == Appointment.SOURCE_EMERGENCY_UNSCHEDULED

        db.drop_all()


def test_all_statuses_remain_visible_in_day_list():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01044000003", "Doctor", "Doctor User")
        patient = create_patient()
        arrived_patient = create_patient(phone_primary="01000000021")
        cancelled_patient = create_patient(phone_primary="01000000022")
        rescheduled_patient = create_patient(phone_primary="01000000023")
        clinic_date = date.today()

        booked = AppointmentService.create_appointment(
            patient_id=arrived_patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        arrived = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_arrived(arrived)

        cancelled = AppointmentService.create_appointment(
            patient_id=cancelled_patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.cancel_appointment(cancelled)

        rescheduled = AppointmentService.create_appointment(
            patient_id=rescheduled_patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.reschedule_appointment(
            rescheduled,
            new_date=clinic_date + timedelta(days=1),
        )

        AppointmentService.close_clinic_day(clinic_date)

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/clinic/day/{clinic_date.isoformat()}")

        assert response.status_code == 200
        assert b"No-show" in response.data
        assert b"Waiting" in response.data
        assert b"Completed" in response.data
        assert b"Cancelled" in response.data
        assert b"Rescheduled" in response.data
        assert booked.status == Appointment.STATUS_NO_SHOW

        db.drop_all()


def test_card_shows_patient_identity_and_actions():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01044000004", "Doctor", "Doctor User")
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/clinic/today", follow_redirects=True)

        assert response.status_code == 200
        assert patient.formatted_mrn.encode() in response.data
        assert b"Sara Ahmed" in response.data
        assert b"data-workspace-url=" in response.data
        assert b"Open Workspace" not in response.data
        assert b"New Visit" in response.data
        assert b"Mark Arrived" not in response.data
        assert b"Manage Booking" not in response.data

        db.drop_all()


def test_today_clinic_shows_active_journey_and_last_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01044000005", "Doctor", "Doctor User")
        patient = create_patient()
        JourneyService.create_journey(
            patient=patient,
            journey_type="gynecology",
            title="Pain follow-up",
            start_date="2026-07-01",
        )
        VisitService.create_visit(
            patient=patient,
            visit_type="gyn",
            visit_date=date(2026, 7, 1),
        )
        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/clinic/today", follow_redirects=True)

        assert response.status_code == 200
        assert b"Gynecology" in response.data
        assert b"Last visit" in response.data
        assert b"Pending flags" in response.data

        db.drop_all()


def test_today_clinic_does_not_create_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01044000006", "Doctor", "Doctor User")
        patient = create_patient()
        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/clinic/today", follow_redirects=True)

        assert response.status_code == 200
        assert patient.visits.count() == 0

        db.drop_all()


def test_close_day_route_converts_remaining_booked_to_no_show():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01044000007", "Reception", "Reception User")
        patient = create_patient()
        arrived_patient = create_patient(phone_primary="01000000031")
        clinic_date = date.today()

        booked = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        arrived = AppointmentService.create_appointment(
            patient_id=arrived_patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_arrived(arrived)

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.post(
                f"/clinic/day/{clinic_date.isoformat()}/close",
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert booked.status == Appointment.STATUS_NO_SHOW
        assert booked.no_show_at is not None
        assert arrived.status == Appointment.STATUS_ARRIVED

        db.drop_all()


def test_today_clinic_has_no_appointment_completion_route():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user(
            "reception@example.com",
            "01044000008",
            "Reception",
            "Reception User",
        )

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        with app.test_client() as client:
            login(
                client,
                "reception@example.com",
            )

            response = client.post(
                f"/clinic/appointments/"
                f"{appointment.uuid}/complete",
                follow_redirects=True,
            )

        assert response.status_code == 404
        assert (
            appointment.status
            == Appointment.STATUS_BOOKED
        )
        assert appointment.visit is None
        assert patient.visits.count() == 0

        db.drop_all()
