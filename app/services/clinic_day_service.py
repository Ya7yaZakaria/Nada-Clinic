
from datetime import UTC, datetime, time, timedelta

from app.models import Appointment, Visit


class ClinicDayService:
    'Read-only clinic-day workflow summaries and live intelligence.'

    LONG_WAIT_MINUTES = 30
    VISIT_TYPE_LABELS = {
        "obs": "Obstetrics",
        "gyn": "Gynecology",
        "infertility": "Infertility",
        "oiti": "Ovulation Induction",
        "iui": "IUI",
        "procedure": "Procedure",
        "general": "General",
    }

    APPOINTMENT_TYPE_LABELS = {
        Appointment.TYPE_NEW_CONSULTATION: "New consultation",
        Appointment.TYPE_FOLLOW_UP: "Follow-up",
        Appointment.TYPE_EMERGENCY: "Emergency",
    }

    @staticmethod
    def _day_bounds(clinic_date):
        start_local = datetime.combine(
            clinic_date,
            time.min,
        )
        end_local = datetime.combine(
            clinic_date + timedelta(days=1),
            time.min,
        )

        return (
            start_local.astimezone(UTC),
            end_local.astimezone(UTC),
        )

    @classmethod
    def get_visit_snapshot(cls, clinic_date):
        start, end = cls._day_bounds(clinic_date)

        visits = (
            Visit.query
            .filter(
                Visit.visit_date >= start,
                Visit.visit_date < end,
            )
            .order_by(
                Visit.visit_date.desc(),
                Visit.id.desc(),
            )
            .all()
        )

        by_patient = {}
        type_counts = {}
        status_counts = {
            "open": 0,
            "completed": 0,
            "incomplete": 0,
        }

        for visit in visits:
            by_patient.setdefault(visit.patient_id, visit)
            status_counts[visit.status] = status_counts.get(visit.status, 0) + 1

            label = cls.VISIT_TYPE_LABELS.get(
                visit.visit_type,
                visit.visit_type.replace("_", " ").title(),
            )
            type_counts[label] = type_counts.get(label, 0) + 1

        return {
            "visits": visits,
            "by_patient": by_patient,
            "total": len(visits),
            "open": status_counts["open"],
            "completed": status_counts["completed"],
            "incomplete": status_counts["incomplete"],
            "type_counts": type_counts,
        }

    @staticmethod
    def build_live_counters(clinic_day, visit_snapshot):
        return {
            "appointments": len(clinic_day["appointments"]),
            "waiting": len(clinic_day["waiting_queue"]),
            "remaining": (
                len(clinic_day["waiting_queue"])
                + len(clinic_day["booked_no_action"])
            ),
            "visits": visit_snapshot["total"],
            "visits_completed": visit_snapshot["completed"],
            "cancelled": clinic_day["counters"]["cancelled"],
        }

    @classmethod
    def waiting_minutes(cls, appointment, now=None):
        if appointment.arrived_at is None:
            return None

        now = now or datetime.now(UTC)
        arrived_at = appointment.arrived_at

        if arrived_at.tzinfo is None:
            arrived_at = arrived_at.replace(tzinfo=UTC)

        return int(max(0, (now - arrived_at).total_seconds()) // 60)

    @staticmethod
    def format_waiting_duration(minutes):
        if minutes is None:
            return None
        if minutes < 60:
            return f"Waiting {minutes} min"

        hours, remaining = divmod(minutes, 60)
        if remaining:
            return f"Waiting {hours} hr {remaining} min"
        return f"Waiting {hours} hr"

    @classmethod
    def build_intelligence(cls, clinic_day, visit_snapshot, now=None):
        now = now or datetime.now(UTC)

        waiting_by_id = {}
        long_wait_count = 0

        for appointment in clinic_day["waiting_queue"]:
            minutes = cls.waiting_minutes(appointment, now=now)
            is_long = minutes is not None and minutes >= cls.LONG_WAIT_MINUTES
            waiting_by_id[appointment.id] = {
                "minutes": minutes,
                "label": cls.format_waiting_duration(minutes),
                "is_long": is_long,
            }
            if is_long:
                long_wait_count += 1

        appointment_type_counts = {
            label: 0
            for label in cls.APPOINTMENT_TYPE_LABELS.values()
        }
        for appointment in clinic_day["appointments"]:
            label = cls.APPOINTMENT_TYPE_LABELS.get(
                appointment.appointment_type,
                appointment.appointment_type.replace("_", " ").title(),
            )
            appointment_type_counts[label] = appointment_type_counts.get(label, 0) + 1

        attended_ids = {
            appointment.id
            for appointment in clinic_day["appointments"]
            if (
                appointment.status == Appointment.STATUS_ARRIVED
                or appointment.visit is not None
            )
        }

        no_show_count = clinic_day["counters"]["no_show"]
        attendance_denominator = len(attended_ids) + no_show_count
        attendance_rate = (
            round((len(attended_ids) / attendance_denominator) * 100, 1)
            if attendance_denominator
            else 0.0
        )

        visit_completion_rate = (
            round(
                (visit_snapshot["completed"] / visit_snapshot["total"]) * 100,
                1,
            )
            if visit_snapshot["total"]
            else 0.0
        )

        alerts = []
        if long_wait_count:
            alerts.append(
                {
                    "kind": "warning",
                    "label": "Long-wait patients",
                    "count": long_wait_count,
                }
            )
        if visit_snapshot["open"]:
            alerts.append(
                {
                    "kind": "info",
                    "label": "Open Visits",
                    "count": visit_snapshot["open"],
                }
            )
        if visit_snapshot["incomplete"]:
            alerts.append(
                {
                    "kind": "warning",
                    "label": "Incomplete Visits",
                    "count": visit_snapshot["incomplete"],
                }
            )

        return {
            "generated_at_utc": now.astimezone(UTC),
            "waiting_by_id": waiting_by_id,
            "alerts": alerts,
            "flow": {
                "scheduled": len(clinic_day["appointments"]),
                "arrived": len(attended_ids),
                "visits": visit_snapshot["total"],
                "completed": visit_snapshot["completed"],
            },
            "appointment_type_counts": appointment_type_counts,
            "visit_type_counts": visit_snapshot["type_counts"],
            "workload": {
                "waiting": len(clinic_day["waiting_queue"]),
                "upcoming": len(clinic_day["booked_no_action"]),
                "open_visits": visit_snapshot["open"],
                "incomplete_visits": visit_snapshot["incomplete"],
                "completed_visits": visit_snapshot["completed"],
            },
            "attendance_rate": attendance_rate,
            "visit_completion_rate": visit_completion_rate,
        }

    @classmethod
    def build_closing_summary(
        cls,
        clinic_day,
        visit_snapshot,
    ):
        visits = visit_snapshot["visits"]

        return {
            "appointments_total": len(
                clinic_day["appointments"]
            ),
            "visits_completed": visit_snapshot[
                "completed"
            ],
            "visits_open": visit_snapshot["open"],
            "visits_incomplete": visit_snapshot[
                "incomplete"
            ],
            "cancelled_count": len(
                clinic_day["cancelled"]
            ),
            "rescheduled_count": len(
                clinic_day["rescheduled"]
            ),
            "no_show_count": len(
                clinic_day["no_show"]
            ),
            "completed_visits": [
                visit
                for visit in visits
                if visit.status == "completed"
            ],
            "open_visits": [
                visit
                for visit in visits
                if visit.status == "open"
            ],
            "incomplete_visits": [
                visit
                for visit in visits
                if visit.status == "incomplete"
            ],
            "cancelled_appointments": (
                clinic_day["cancelled"]
            ),
            "rescheduled_appointments": (
                clinic_day["rescheduled"]
            ),
            "no_show_appointments": (
                clinic_day["no_show"]
            ),
        }
    @staticmethod
    def is_close_result_visible(clinic_day):
        counters = clinic_day["counters"]
        return (
            counters["booked"] == 0
            and counters["arrived"] == 0
            and counters["no_show"] > 0
        )
