from datetime import UTC, date, datetime

from app.extensions import db
from app.models.appointment import Appointment


class AppointmentService:
    TYPE_LABELS = {
        Appointment.TYPE_NEW_CONSULTATION: "كشف",
        Appointment.TYPE_FOLLOW_UP: "إعادة كشف",
        Appointment.TYPE_EMERGENCY: "طوارئ",
    }

    STATUS_LABELS = {
        Appointment.STATUS_BOOKED: "Booked",
        Appointment.STATUS_ARRIVED: "Waiting",
        Appointment.STATUS_COMPLETED: "Completed",
        Appointment.STATUS_CANCELLED: "Cancelled",
        Appointment.STATUS_RESCHEDULED: "Rescheduled",
        Appointment.STATUS_NO_SHOW: "No-show",
    }

    SOURCE_LABELS = {
        Appointment.SOURCE_PHONE: "Phone",
        Appointment.SOURCE_WHATSAPP: "WhatsApp",
        Appointment.SOURCE_CLINIC: "Clinic",
        Appointment.SOURCE_EMERGENCY_UNSCHEDULED: "Emergency unscheduled",
    }

    @staticmethod
    def validate_appointment_type(appointment_type):
        if appointment_type not in Appointment.VALID_TYPES:
            raise ValueError("Invalid appointment type")
        return True

    @staticmethod
    def validate_status(status):
        if status not in Appointment.VALID_STATUSES:
            raise ValueError("Invalid appointment status")
        return True

    @staticmethod
    def validate_source(source):
        if source not in Appointment.VALID_SOURCES:
            raise ValueError("Invalid appointment source")
        return True

    @classmethod
    def create_appointment(
        cls,
        *,
        patient_id,
        appointment_date,
        appointment_time=None,
        duration_minutes=None,
        appointment_type,
        status=None,
        source=None,
        notes=None,
        created_by_user_id=None,
    ):
        if not patient_id:
            raise ValueError("Appointment must belong to a patient")

        if appointment_date is None:
            raise ValueError("Appointment date is required")

        cls.validate_appointment_type(appointment_type)

        status = status or Appointment.STATUS_BOOKED
        source = source or Appointment.SOURCE_CLINIC

        cls.validate_status(status)
        cls.validate_source(source)

        appointment = Appointment(
            patient_id=patient_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            duration_minutes=duration_minutes,
            appointment_type=appointment_type,
            status=status,
            source=source,
            notes=notes,
            created_by_user_id=created_by_user_id,
        )

        db.session.add(appointment)
        db.session.commit()
        return appointment

    @classmethod
    def update_appointment(cls, appointment, **kwargs):
        for key in (
            "appointment_date",
            "appointment_time",
            "duration_minutes",
            "notes",
            "updated_by_user_id",
        ):
            if key in kwargs:
                setattr(appointment, key, kwargs[key])

        if "appointment_type" in kwargs:
            cls.validate_appointment_type(kwargs["appointment_type"])
            appointment.appointment_type = kwargs["appointment_type"]

        if "source" in kwargs:
            cls.validate_source(kwargs["source"])
            appointment.source = kwargs["source"]

        db.session.commit()
        return appointment

    @staticmethod
    def mark_arrived(appointment):
        appointment.status = Appointment.STATUS_ARRIVED
        appointment.arrived_at = datetime.now(UTC)
        db.session.commit()
        return appointment

    @staticmethod
    def mark_completed(appointment):
        appointment.status = Appointment.STATUS_COMPLETED
        appointment.completed_at = datetime.now(UTC)
        db.session.commit()
        return appointment

    @staticmethod
    def cancel_appointment(appointment, reason=None):
        appointment.status = Appointment.STATUS_CANCELLED
        appointment.cancel_reason = reason
        appointment.cancelled_at = datetime.now(UTC)
        db.session.commit()
        return appointment

    @staticmethod
    def mark_no_show(appointment):
        appointment.status = Appointment.STATUS_NO_SHOW
        appointment.no_show_at = datetime.now(UTC)
        db.session.commit()
        return appointment

    @classmethod
    def reschedule_appointment(cls, appointment, *, new_date, new_time=None, updated_by_user_id=None):
        new_appointment = Appointment(
            patient_id=appointment.patient_id,
            appointment_date=new_date,
            appointment_time=new_time,
            appointment_type=appointment.appointment_type,
            status=Appointment.STATUS_BOOKED,
            source=appointment.source,
            notes=appointment.notes,
            created_by_user_id=appointment.created_by_user_id,
            updated_by_user_id=updated_by_user_id,
            rescheduled_from=appointment,
        )

        db.session.add(new_appointment)
        db.session.flush()

        appointment.status = Appointment.STATUS_RESCHEDULED
        appointment.rescheduled_at = datetime.now(UTC)
        appointment.rescheduled_to = new_appointment
        appointment.updated_by_user_id = updated_by_user_id

        db.session.commit()
        return new_appointment

    @classmethod
    def create_emergency_unscheduled(cls, *, patient_id, notes=None, created_by_user_id=None):
        appointment = cls.create_appointment(
            patient_id=patient_id,
            appointment_date=date.today(),
            appointment_time=None,
            appointment_type=Appointment.TYPE_EMERGENCY,
            status=Appointment.STATUS_BOOKED,
            source=Appointment.SOURCE_EMERGENCY_UNSCHEDULED,
            notes=notes,
            created_by_user_id=created_by_user_id,
        )

        return cls.mark_arrived(appointment)

    @staticmethod
    def close_clinic_day(clinic_date):
        appointments = Appointment.query.filter_by(
            appointment_date=clinic_date,
            status=Appointment.STATUS_BOOKED,
        ).all()

        now = datetime.now(UTC)
        for appointment in appointments:
            appointment.status = Appointment.STATUS_NO_SHOW
            appointment.no_show_at = now

        db.session.commit()
        return appointments

    @staticmethod
    def get_patient_appointments(patient_id):
        return Appointment.query.filter_by(patient_id=patient_id).order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc(),
        ).all()

    @staticmethod
    def get_appointments_for_date(clinic_date):
        return Appointment.query.filter_by(appointment_date=clinic_date).order_by(
            Appointment.appointment_time.asc().nullslast(),
            Appointment.created_at.asc(),
        ).all()

    @classmethod
    def get_today_appointments(cls):
        return cls.get_appointments_for_date(date.today())

    @staticmethod
    def get_appointments_between_dates(start_date, end_date):
        return Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date,
        ).order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc().nullslast(),
            Appointment.created_at.asc(),
        ).all()

    @classmethod
    def get_calendar_counts(cls, start_date, end_date):
        appointments = cls.get_appointments_between_dates(start_date, end_date)
        counts = {}

        for appointment in appointments:
            counts[appointment.appointment_date] = counts.get(appointment.appointment_date, 0) + 1

        return counts

    @staticmethod
    def get_total_booked_for_date(clinic_date):
        return Appointment.query.filter_by(appointment_date=clinic_date).count()

    @staticmethod
    def get_counters_for_date(clinic_date):
        appointments = Appointment.query.filter_by(appointment_date=clinic_date).all()

        counters = {
            "total_booked_today": len(appointments),
            "booked": 0,
            "arrived": 0,
            "completed": 0,
            "cancelled": 0,
            "rescheduled": 0,
            "no_show": 0,
            "emergency": 0,
        }

        for appointment in appointments:
            if appointment.status in counters:
                counters[appointment.status] += 1
            if appointment.appointment_type == Appointment.TYPE_EMERGENCY:
                counters["emergency"] += 1

        return counters

    @staticmethod
    def get_waiting_queue(clinic_date=None):
        clinic_date = clinic_date or date.today()

        return Appointment.query.filter_by(
            appointment_date=clinic_date,
            status=Appointment.STATUS_ARRIVED,
        ).order_by(
            Appointment.arrived_at.asc().nullslast(),
            Appointment.appointment_time.asc().nullslast(),
            Appointment.created_at.asc(),
        ).all()


    @staticmethod
    def get_booked_no_action(clinic_date):
        return Appointment.query.filter_by(
            appointment_date=clinic_date,
            status=Appointment.STATUS_BOOKED,
        ).order_by(
            Appointment.appointment_time.asc().nullslast(),
            Appointment.created_at.asc(),
        ).all()

    @staticmethod
    def get_completed_for_date(clinic_date):
        return Appointment.query.filter_by(
            appointment_date=clinic_date,
            status=Appointment.STATUS_COMPLETED,
        ).order_by(
            Appointment.completed_at.asc().nullslast(),
            Appointment.appointment_time.asc().nullslast(),
            Appointment.created_at.asc(),
        ).all()

    @staticmethod
    def get_cancelled_for_date(clinic_date):
        return Appointment.query.filter_by(
            appointment_date=clinic_date,
            status=Appointment.STATUS_CANCELLED,
        ).order_by(
            Appointment.cancelled_at.asc().nullslast(),
            Appointment.appointment_time.asc().nullslast(),
            Appointment.created_at.asc(),
        ).all()

    @staticmethod
    def get_rescheduled_for_date(clinic_date):
        return Appointment.query.filter_by(
            appointment_date=clinic_date,
            status=Appointment.STATUS_RESCHEDULED,
        ).order_by(
            Appointment.rescheduled_at.asc().nullslast(),
            Appointment.appointment_time.asc().nullslast(),
            Appointment.created_at.asc(),
        ).all()

    @staticmethod
    def get_no_show_for_date(clinic_date):
        return Appointment.query.filter_by(
            appointment_date=clinic_date,
            status=Appointment.STATUS_NO_SHOW,
        ).order_by(
            Appointment.no_show_at.asc().nullslast(),
            Appointment.appointment_time.asc().nullslast(),
            Appointment.created_at.asc(),
        ).all()

    @classmethod
    def get_clinic_day(cls, clinic_date):
        appointments = cls.get_appointments_for_date(clinic_date)

        return {
            "clinic_date": clinic_date,
            "appointments": appointments,
            "counters": cls.get_counters_for_date(clinic_date),
            "waiting_queue": cls.get_waiting_queue(clinic_date),
            "booked_no_action": cls.get_booked_no_action(clinic_date),
            "completed": cls.get_completed_for_date(clinic_date),
            "cancelled": cls.get_cancelled_for_date(clinic_date),
            "rescheduled": cls.get_rescheduled_for_date(clinic_date),
            "no_show": cls.get_no_show_for_date(clinic_date),
        }

    @classmethod
    def get_today_clinic(cls):
        return cls.get_clinic_day(date.today())


    @classmethod
    def get_unfinished_for_date(cls, clinic_date):
        return Appointment.query.filter(
            Appointment.appointment_date == clinic_date,
            Appointment.status.in_([
                Appointment.STATUS_BOOKED,
                Appointment.STATUS_ARRIVED,
            ]),
        ).order_by(
            Appointment.status.asc(),
            Appointment.appointment_time.asc().nullslast(),
            Appointment.created_at.asc(),
        ).all()

    @classmethod
    def get_day_summary(cls, clinic_date):
        clinic_day = cls.get_clinic_day(clinic_date)

        clinic_day["unfinished"] = cls.get_unfinished_for_date(clinic_date)
        clinic_day["arrived_not_completed"] = cls.get_waiting_queue(clinic_date)
        clinic_day["is_previous_day"] = clinic_date < date.today()

        return clinic_day

    @classmethod
    def get_previous_clinic_days(cls, limit=30):
        rows = (
            db.session.query(Appointment.appointment_date)
            .filter(Appointment.appointment_date < date.today())
            .distinct()
            .order_by(Appointment.appointment_date.desc())
            .limit(limit)
            .all()
        )

        summaries = []
        for row in rows:
            clinic_date = row[0]
            summaries.append(cls.get_day_summary(clinic_date))

        return summaries

    @staticmethod
    def get_status_label(status):
        return AppointmentService.STATUS_LABELS.get(status, status)

    @staticmethod
    def get_type_label(appointment_type):
        return AppointmentService.TYPE_LABELS.get(appointment_type, appointment_type)

    @staticmethod
    def get_source_label(source):
        return AppointmentService.SOURCE_LABELS.get(source, source)
