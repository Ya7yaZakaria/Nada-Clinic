from datetime import date, timedelta

import pytest

from app import create_app
from app.extensions import db
from app.models import Patient
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
from app.services.patient_service import PatientService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


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


def test_appointment_can_be_created():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        assert appointment.id is not None
        assert appointment.uuid is not None
        assert appointment.patient_id == patient.id
        assert appointment.status == Appointment.STATUS_BOOKED
        assert appointment.source == Appointment.SOURCE_CLINIC

        db.drop_all()


def test_appointment_belongs_to_patient():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        saved_appointment = db.session.get(Appointment, appointment.id)

        assert saved_appointment.patient_id == patient.id
        assert saved_appointment.patient.id == patient.id

        db.drop_all()


def test_appointment_uuid_is_generated():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        assert appointment.uuid is not None
        assert len(appointment.uuid) == 36

        db.drop_all()


def test_appointment_date_is_required():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        with pytest.raises(ValueError, match="Appointment date is required"):
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=None,
                appointment_type=Appointment.TYPE_NEW_CONSULTATION,
            )

        db.drop_all()


def test_appointment_time_is_optional():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_time=None,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        assert appointment.appointment_time is None

        db.drop_all()


def test_appointment_type_is_required():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        with pytest.raises(ValueError, match="Invalid appointment type"):
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=None,
            )

        db.drop_all()


def test_invalid_type_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        with pytest.raises(ValueError, match="Invalid appointment type"):
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type="invalid",
            )

        db.drop_all()


def test_procedure_type_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        with pytest.raises(ValueError, match="Invalid appointment type"):
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type="procedure",
            )

        db.drop_all()


def test_status_defaults_to_booked():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        assert appointment.status == Appointment.STATUS_BOOKED

        db.drop_all()


def test_source_defaults_to_clinic():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        assert appointment.source == Appointment.SOURCE_CLINIC

        db.drop_all()


def test_invalid_status_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        with pytest.raises(ValueError, match="Invalid appointment status"):
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=Appointment.TYPE_NEW_CONSULTATION,
                status="in_consultation",
            )

        db.drop_all()


def test_invalid_source_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        with pytest.raises(ValueError, match="Invalid appointment source"):
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=Appointment.TYPE_NEW_CONSULTATION,
                source="online_booking",
            )

        db.drop_all()


def test_emergency_unscheduled_is_arrived_without_time():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_emergency_unscheduled(patient_id=patient.id)

        assert appointment.appointment_type == Appointment.TYPE_EMERGENCY
        assert appointment.source == Appointment.SOURCE_EMERGENCY_UNSCHEDULED
        assert appointment.status == Appointment.STATUS_ARRIVED
        assert appointment.appointment_time is None
        assert appointment.arrived_at is not None

        db.drop_all()


def test_appointment_does_not_create_visit():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        assert hasattr(patient, "visits")
        assert patient.visits.count() == 0

        db.drop_all()


def test_mark_arrived_sets_status_and_timestamp():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        AppointmentService.mark_arrived(appointment)

        assert appointment.status == Appointment.STATUS_ARRIVED
        assert appointment.arrived_at is not None

        db.drop_all()


def test_mark_completed_sets_status_and_timestamp():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        AppointmentService.mark_completed(appointment)

        assert appointment.status == Appointment.STATUS_COMPLETED
        assert appointment.completed_at is not None

        db.drop_all()


def test_cancel_sets_status_and_timestamp():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        AppointmentService.cancel_appointment(appointment, reason="Patient called")

        assert appointment.status == Appointment.STATUS_CANCELLED
        assert appointment.cancelled_at is not None
        assert appointment.cancel_reason == "Patient called"

        db.drop_all()


def test_reschedule_sets_old_status_and_creates_new_appointment():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        old_appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        new_appointment = AppointmentService.reschedule_appointment(
            old_appointment,
            new_date=date.today() + timedelta(days=1),
        )

        assert old_appointment.status == Appointment.STATUS_RESCHEDULED
        assert old_appointment.rescheduled_at is not None
        assert old_appointment.rescheduled_to_id == new_appointment.id
        assert new_appointment.rescheduled_from_id == old_appointment.id
        assert new_appointment.status == Appointment.STATUS_BOOKED

        db.drop_all()


def test_mark_no_show_sets_status_and_timestamp():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        AppointmentService.mark_no_show(appointment)

        assert appointment.status == Appointment.STATUS_NO_SHOW
        assert appointment.no_show_at is not None

        db.drop_all()


def test_close_clinic_day_converts_only_booked_to_no_show():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()
        clinic_date = date.today()

        booked = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        arrived = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
            source=Appointment.SOURCE_PHONE,
        )
        AppointmentService.mark_arrived(arrived)

        completed = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
            source=Appointment.SOURCE_WHATSAPP,
        )
        AppointmentService.mark_completed(completed)

        converted = AppointmentService.close_clinic_day(clinic_date)

        assert booked in converted
        assert booked.status == Appointment.STATUS_NO_SHOW
        assert booked.no_show_at is not None
        assert arrived.status == Appointment.STATUS_ARRIVED
        assert completed.status == Appointment.STATUS_COMPLETED

        db.drop_all()


def test_total_booked_counts_all_statuses_for_date():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()
        clinic_date = date.today()

        booked = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        arrived = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
            source=Appointment.SOURCE_PHONE,
        )
        AppointmentService.mark_arrived(arrived)

        cancelled = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_FOLLOW_UP,
            source=Appointment.SOURCE_WHATSAPP,
        )
        AppointmentService.cancel_appointment(cancelled)

        assert AppointmentService.get_total_booked_for_date(clinic_date) == 3

        counters = AppointmentService.get_counters_for_date(clinic_date)

        assert counters["total_booked_today"] == 3
        assert counters["booked"] == 1
        assert counters["arrived"] == 1
        assert counters["cancelled"] == 1

        db.drop_all()


def test_counters_work_for_date():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()
        clinic_date = date.today()

        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=clinic_date,
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        emergency = AppointmentService.create_emergency_unscheduled(patient_id=patient.id)

        counters = AppointmentService.get_counters_for_date(clinic_date)

        assert counters["total_booked_today"] == 2
        assert counters["booked"] == 1
        assert counters["arrived"] == 1
        assert counters["emergency"] == 1
        assert emergency.appointment_type == Appointment.TYPE_EMERGENCY

        db.drop_all()
