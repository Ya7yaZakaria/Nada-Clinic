from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.extensions import db
from app.models import Appointment, Patient, User, Visit
from app.services.appointment_service import AppointmentService
from app.services.rbac_service import RBACService
from app.services.visit_service import VisitService


def create_patient(number=1):
    patient = Patient(medical_file_number=number, name_ar="مريضة", name_en=f"Patient {number}", search_name=f"patient {number}", gender="female", phone_primary=f"010000{number:05d}")
    db.session.add(patient)
    db.session.commit()
    return patient


def login_doctor(app, client, suffix):
    user = User(
        email=f"visit-link-{suffix}@example.com",
        phone=f"01077{suffix:06d}",
        name="Visit Link Doctor",
    )
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()
    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, "Doctor")
    return client.post(
        "/auth/login",
        data={
            "login_identifier": user.email,
            "password": "12345678",
        },
    )


def test_active_daily_duplicate_and_history_rebooking():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        patient = create_patient()
        first = AppointmentService.create_appointment(patient_id=patient.id, appointment_date=date.today(), appointment_type=Appointment.TYPE_NEW_CONSULTATION)
        with pytest.raises(ValueError, match="active appointment"):
            AppointmentService.create_appointment(patient_id=patient.id, appointment_date=date.today(), appointment_type=Appointment.TYPE_FOLLOW_UP)
        AppointmentService.cancel_appointment(first)
        replacement = AppointmentService.create_appointment(patient_id=patient.id, appointment_date=date.today(), appointment_type=Appointment.TYPE_FOLLOW_UP)
        assert replacement.status == Appointment.STATUS_BOOKED
        db.drop_all()


def test_visit_links_appointment_and_prevents_duplicate():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        patient = create_patient()
        appointment = AppointmentService.create_appointment(patient_id=patient.id, appointment_date=date.today(), appointment_type=Appointment.TYPE_NEW_CONSULTATION)
        visit = VisitService.create_visit(patient=patient, appointment=appointment, visit_type="general")
        assert visit.appointment is appointment
        assert appointment.visit is visit
        assert appointment.status == Appointment.STATUS_ARRIVED
        with pytest.raises(ValueError, match="already has a Visit"):
            VisitService.create_visit(patient=patient, appointment=appointment, visit_type="general")
        db.drop_all()


def test_visit_rejects_appointment_for_another_patient():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        first, second = create_patient(1), create_patient(2)
        appointment = AppointmentService.create_appointment(patient_id=first.id, appointment_date=date.today(), appointment_type=Appointment.TYPE_NEW_CONSULTATION)
        with pytest.raises(ValueError, match="another patient"):
            VisitService.create_visit(patient=second, appointment=appointment, visit_type="general")
        db.drop_all()


def test_resolved_bookings_filter_and_sort_by_resolution_timestamp():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        completed_patient, cancelled_patient, rescheduled_patient, no_show_patient = (create_patient(i) for i in range(1, 5))
        completed_appointment = AppointmentService.create_appointment(patient_id=completed_patient.id, appointment_date=date.today(), appointment_type=Appointment.TYPE_NEW_CONSULTATION)
        visit = VisitService.create_visit(patient=completed_patient, appointment=completed_appointment, visit_type="general")
        VisitService.complete_visit(visit, confirmed=True)
        cancelled = AppointmentService.create_appointment(patient_id=cancelled_patient.id, appointment_date=date.today(), appointment_type=Appointment.TYPE_FOLLOW_UP)
        AppointmentService.cancel_appointment(cancelled)
        rescheduled = AppointmentService.create_appointment(patient_id=rescheduled_patient.id, appointment_date=date.today(), appointment_type=Appointment.TYPE_FOLLOW_UP)
        AppointmentService.reschedule_appointment(rescheduled, new_date=date.today() + timedelta(days=1))
        no_show = AppointmentService.create_appointment(patient_id=no_show_patient.id, appointment_date=date.today(), appointment_type=Appointment.TYPE_FOLLOW_UP)
        AppointmentService.mark_no_show(no_show)
        base = datetime.now(timezone.utc)
        visit.completed_at, cancelled.cancelled_at, rescheduled.rescheduled_at = base, base + timedelta(minutes=1), base + timedelta(minutes=2)
        db.session.commit()
        latest = AppointmentService.get_resolved_bookings(date.today(), "all", "latest")
        assert [item["kind"] for item in latest["items"]] == ["rescheduled", "cancelled", "completed"]
        oldest = AppointmentService.get_resolved_bookings(date.today(), "all", "oldest")
        assert [item["kind"] for item in oldest["items"]] == ["completed", "cancelled", "rescheduled"]
        assert [item["kind"] for item in AppointmentService.get_resolved_bookings(date.today(), "cancelled")["items"]] == ["cancelled"]
        db.drop_all()


def test_active_daily_rule_covers_update_reschedule_emergency_and_self_edit():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        patient = create_patient()
        today = date.today()
        first = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=today,
            appointment_time=datetime.strptime("09:00", "%H:%M").time(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )
        AppointmentService.update_appointment(
            first,
            appointment_date=today,
            appointment_time=datetime.strptime("10:00", "%H:%M").time(),
        )

        other = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=today + timedelta(days=1),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        with pytest.raises(ValueError, match="active appointment"):
            AppointmentService.update_appointment(other, appointment_date=today)
        assert other.appointment_date == today + timedelta(days=1)

        with pytest.raises(ValueError, match="active appointment"):
            AppointmentService.reschedule_appointment(
                other,
                new_date=today,
            )
        assert other.status == Appointment.STATUS_BOOKED
        assert other.rescheduled_to is None

        with pytest.raises(ValueError, match="active appointment"):
            AppointmentService.create_emergency_unscheduled(
                patient_id=patient.id,
            )

        AppointmentService.reschedule_appointment(
            first,
            new_date=today + timedelta(days=2),
        )
        replacement = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=today,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        assert replacement.status == Appointment.STATUS_BOOKED
        db.drop_all()


@pytest.mark.parametrize(
    "status",
    [
        Appointment.STATUS_CANCELLED,
        Appointment.STATUS_RESCHEDULED,
        Appointment.STATUS_NO_SHOW,
    ],
)
def test_visit_rejects_resolved_appointment_statuses(status):
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
            status=status,
        )
        with pytest.raises(ValueError, match="booked or arrived"):
            VisitService.create_visit(
                patient=patient,
                appointment=appointment,
                visit_type="general",
            )
        db.drop_all()


def test_visit_from_arrived_and_standalone_visit_are_preserved():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )
        AppointmentService.mark_arrived(appointment)
        arrived_at = appointment.arrived_at
        linked = VisitService.create_visit(
            patient=patient,
            appointment=appointment,
            visit_type="general",
        )
        standalone = VisitService.create_visit(
            patient=patient,
            visit_type="general",
        )
        assert linked.appointment_id == appointment.id
        assert appointment.arrived_at == arrived_at
        assert standalone.appointment_id is None
        db.drop_all()


def test_database_unique_constraint_prevents_second_visit_link():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )
        db.session.add_all(
            [
                Visit(patient_id=patient.id, appointment_id=appointment.id),
                Visit(patient_id=patient.id, appointment_id=appointment.id),
            ]
        )
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        db.drop_all()


def test_resolved_defaults_filters_tie_break_and_appointment_time_independence():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        first_patient = create_patient(10)
        second_patient = create_patient(11)
        first = AppointmentService.create_appointment(
            patient_id=first_patient.id,
            appointment_date=date.today(),
            appointment_time=datetime.strptime("18:00", "%H:%M").time(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        second = AppointmentService.create_appointment(
            patient_id=second_patient.id,
            appointment_date=date.today(),
            appointment_time=datetime.strptime("08:00", "%H:%M").time(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )
        AppointmentService.cancel_appointment(first)
        AppointmentService.cancel_appointment(second)
        resolved_at = datetime.now(timezone.utc)
        first.cancelled_at = resolved_at
        second.cancelled_at = resolved_at
        db.session.commit()

        latest = AppointmentService.get_resolved_bookings(
            date.today(), "invalid", "invalid"
        )
        assert latest["filter"] == "all"
        assert latest["sort"] == "latest"
        assert [row["appointment"].id for row in latest["items"]] == [
            second.id,
            first.id,
        ]
        oldest = AppointmentService.get_resolved_bookings(
            date.today(), "cancelled", "oldest"
        )
        assert [row["appointment"].id for row in oldest["items"]] == [
            first.id,
            second.id,
        ]
        assert AppointmentService.get_resolved_bookings(
            date.today(), "completed"
        )["items"] == []
        assert AppointmentService.get_resolved_bookings(
            date.today(), "rescheduled"
        )["items"] == []
        db.drop_all()


def test_visit_route_accepts_appointment_uuid_and_preserves_it_on_form_error():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    with app.app_context():
        db.create_all()
        patient = create_patient(20)
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )
        client = app.test_client()
        login_doctor(app, client, 20)

        invalid = client.post(
            f"/patients/{patient.uuid}/visits/new",
            data={
                "appointment_uuid": appointment.uuid,
                "visit_type": "invalid",
            },
        )
        assert invalid.status_code == 200
        assert b'name="appointment_uuid"' in invalid.data
        assert appointment.uuid.encode() in invalid.data
        assert appointment.visit is None

        created = client.post(
            f"/patients/{patient.uuid}/visits/new",
            data={
                "appointment_uuid": appointment.uuid,
                "visit_type": "general",
                "journey_id": "",
                "billing_service_type": "",
                "payment_method": "",
            },
        )
        assert created.status_code == 302
        assert appointment.visit is not None
        assert appointment.status == Appointment.STATUS_ARRIVED
        db.drop_all()


def test_visit_route_rejects_appointment_patient_mismatch():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    with app.app_context():
        db.create_all()
        owner = create_patient(21)
        other = create_patient(22)
        appointment = AppointmentService.create_appointment(
            patient_id=owner.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )
        client = app.test_client()
        login_doctor(app, client, 21)
        response = client.get(
            f"/patients/{other.uuid}/visits/new?appointment_uuid={appointment.uuid}"
        )
        assert response.status_code == 404
        db.drop_all()
