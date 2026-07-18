from datetime import UTC, datetime, time, timedelta

from app.models import Visit


class ClinicDayService:
    """Read-only clinic-day workflow summaries."""

    VISIT_TYPE_LABELS = {
        "obs": "Obstetrics",
        "gyn": "Gynecology",
        "infertility": "Infertility",
        "oiti": "Ovulation Induction",
        "iui": "IUI",
        "procedure": "Procedure",
        "general": "General",
    }

    @staticmethod
    def _day_bounds(clinic_date):
        start = datetime.combine(
            clinic_date,
            time.min,
            tzinfo=UTC,
        )

        return start, start + timedelta(days=1)

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
            by_patient.setdefault(
                visit.patient_id,
                visit,
            )

            status_counts[visit.status] = (
                status_counts.get(visit.status, 0)
                + 1
            )

            label = cls.VISIT_TYPE_LABELS.get(
                visit.visit_type,
                visit.visit_type.replace(
                    "_",
                    " ",
                ).title(),
            )

            type_counts[label] = (
                type_counts.get(label, 0)
                + 1
            )

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
    def build_live_counters(
        clinic_day,
        visit_snapshot,
    ):
        return {
            "appointments": len(
                clinic_day["appointments"]
            ),
            "waiting": len(clinic_day["waiting_queue"]),
            "remaining": (
                len(clinic_day["waiting_queue"])
                + len(clinic_day["booked_no_action"])
            ),
            "visits": visit_snapshot["total"],
            "visits_completed": (
                visit_snapshot["completed"]
            ),
            "cancelled": clinic_day["counters"]["cancelled"],
        }

    @staticmethod
    def is_close_result_visible(clinic_day):
        counters = clinic_day["counters"]

        return (
            counters["booked"] == 0
            and counters["arrived"] == 0
            and counters["no_show"] > 0
        )
