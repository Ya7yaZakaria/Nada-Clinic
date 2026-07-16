from datetime import date, datetime, time, timezone

from app.models import Patient, Visit
from app.services.appointment_service import AppointmentService


class DashboardService:
    @staticmethod
    def get_today_summary():
        clinic_day = AppointmentService.get_today_clinic()
        start = datetime.combine(date.today(), time.min, tzinfo=timezone.utc)
        end = datetime.combine(date.today(), time.max, tzinfo=timezone.utc)
        open_visits = Visit.query.filter(
            Visit.visit_date >= start,
            Visit.visit_date <= end,
            Visit.status == "open",
        ).count()
        counters = clinic_day["counters"]
        return {
            "date": date.today(),
            "appointments": counters["total_booked_today"],
            "waiting": counters["arrived"],
            "completed": counters["completed"],
            "open_visits": open_visits,
        }

    @staticmethod
    def get_recent_patients(limit=5):
        return (
            Patient.query.filter_by(is_active=True)
            .order_by(Patient.updated_at.desc(), Patient.id.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_recent_visits(limit=5):
        return (
            Visit.query.order_by(Visit.visit_date.desc(), Visit.id.desc())
            .limit(limit)
            .all()
        )
