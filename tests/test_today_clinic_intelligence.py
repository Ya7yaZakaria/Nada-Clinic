
from datetime import date, datetime, timedelta, timezone

from app import create_app
from app.extensions import db
from app.models import Appointment, Patient, User
from app.services.appointment_service import AppointmentService
from app.services.clinic_day_service import ClinicDayService
from app.services.finance_service import FinanceService
from app.services.rbac_service import RBACService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
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


def create_patient(number):
    patient = Patient(
        medical_file_number=number,
        name_ar="Test Patient",
        name_en=f"Patient {number}",
        search_name=f"patient {number}",
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


def test_waiting_duration_boundary_and_formatting():
    app = make_app()

    with app.app_context():
        db.create_all()
        patient = create_patient(91001)
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_arrived(appointment)

        now = datetime.now(timezone.utc)
        appointment.arrived_at = now - timedelta(minutes=29)
        db.session.commit()

        intelligence = ClinicDayService.build_intelligence(
            AppointmentService.get_clinic_day(date.today()),
            ClinicDayService.get_visit_snapshot(date.today()),
            now=now,
        )
        info = intelligence["waiting_by_id"][appointment.id]
        assert info["minutes"] == 29
        assert info["is_long"] is False
        assert info["label"] == "Waiting 29 min"

        appointment.arrived_at = now - timedelta(minutes=72)
        db.session.commit()

        intelligence = ClinicDayService.build_intelligence(
            AppointmentService.get_clinic_day(date.today()),
            ClinicDayService.get_visit_snapshot(date.today()),
            now=now,
        )
        info = intelligence["waiting_by_id"][appointment.id]
        assert info["minutes"] == 72
        assert info["is_long"] is True
        assert info["label"] == "Waiting 1 hr 12 min"

        db.drop_all()


def test_negative_waiting_duration_is_zero():
    app = make_app()

    with app.app_context():
        db.create_all()
        patient = create_patient(91002)
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.mark_arrived(appointment)

        now = datetime.now(timezone.utc)
        appointment.arrived_at = now + timedelta(minutes=5)
        db.session.commit()

        assert ClinicDayService.waiting_minutes(appointment, now=now) == 0
        db.drop_all()


def test_flow_breakdown_alerts_and_rates():
    app = make_app()

    with app.app_context():
        db.create_all()
        now = datetime.now(timezone.utc)

        waiting_patient = create_patient(91011)
        completed_patient = create_patient(91012)
        no_show_patient = create_patient(91013)

        waiting = AppointmentService.create_appointment(
            patient_id=waiting_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )
        AppointmentService.mark_arrived(waiting)
        waiting.arrived_at = now - timedelta(minutes=45)

        completed_appointment = AppointmentService.create_appointment(
            patient_id=completed_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        completed_visit = VisitService.create_visit(
            patient=completed_patient,
            appointment=completed_appointment,
            visit_type="gyn",
        )
        VisitService.complete_visit(completed_visit, confirmed=True)

        no_show = AppointmentService.create_appointment(
            patient_id=no_show_patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_EMERGENCY,
        )
        AppointmentService.mark_no_show(no_show)
        db.session.commit()

        intelligence = ClinicDayService.build_intelligence(
            AppointmentService.get_clinic_day(date.today()),
            ClinicDayService.get_visit_snapshot(date.today()),
            now=now,
        )

        assert intelligence["flow"] == {
            "scheduled": 3,
            "arrived": 2,
            "visits": 1,
            "completed": 1,
        }
        assert intelligence["attendance_rate"] == 66.7
        assert intelligence["visit_completion_rate"] == 100.0
        assert intelligence["appointment_type_counts"]["New consultation"] == 1
        assert intelligence["appointment_type_counts"]["Follow-up"] == 1
        assert intelligence["appointment_type_counts"]["Emergency"] == 1
        assert intelligence["visit_type_counts"]["Gynecology"] == 1
        assert any(
            alert["label"] == "Long-wait patients"
            for alert in intelligence["alerts"]
        )

        db.drop_all()


def test_empty_day_rates_are_zero():
    app = make_app()

    with app.app_context():
        db.create_all()
        intelligence = ClinicDayService.build_intelligence(
            AppointmentService.get_clinic_day(date.today()),
            ClinicDayService.get_visit_snapshot(date.today()),
        )

        assert intelligence["attendance_rate"] == 0.0
        assert intelligence["visit_completion_rate"] == 0.0
        assert intelligence["alerts"] == []
        db.drop_all()


def test_reception_does_not_query_finance(monkeypatch):
    app = make_app()

    def forbidden(*args, **kwargs):
        raise AssertionError("Reception invoked FinanceService.get_insights_summary")

    monkeypatch.setattr(
        FinanceService,
        "get_insights_summary",
        forbidden,
    )

    with app.app_context():
        db.create_all()
        create_user(
            "Reception",
            "clinic-intelligence-reception@example.com",
            "01091000001",
        )

        client = app.test_client()
        login(client, "clinic-intelligence-reception@example.com")
        response = client.get(f"/clinic/day/{date.today().isoformat()}")

        assert response.status_code == 200
        assert b"Live Finance" not in response.data
        assert b"clinic-live-clock" in response.data
        assert b'data-timezone="Africa/Cairo"' in response.data
        assert b"clinic-last-updated" in response.data
        assert b"Clinic Workload" in response.data

        db.drop_all()


def test_doctor_receives_finance_and_live_markers(monkeypatch):
    app = make_app()
    called = {"value": False}
    original = FinanceService.get_insights_summary

    def tracked(*args, **kwargs):
        called["value"] = True
        return original(*args, **kwargs)

    monkeypatch.setattr(
        FinanceService,
        "get_insights_summary",
        tracked,
    )

    with app.app_context():
        db.create_all()
        create_user(
            "Doctor",
            "clinic-intelligence-doctor@example.com",
            "01091000002",
        )

        client = app.test_client()
        login(client, "clinic-intelligence-doctor@example.com")
        response = client.get(f"/clinic/day/{date.today().isoformat()}")

        assert response.status_code == 200
        assert called["value"] is True
        assert b"Live Finance" in response.data
        assert b"Visits Started" in response.data
        assert b"Attendance rate" in response.data
        assert b"Refresh" in response.data

        db.drop_all()
