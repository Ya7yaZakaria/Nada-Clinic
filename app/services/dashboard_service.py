from collections import Counter
from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)

from sqlalchemy import func

from app.models import Appointment, Journey, Patient, Visit
from app.services.appointment_service import AppointmentService
from app.services.finance_service import FinanceService


class DashboardService:
    PRESETS = {
        "today",
        "last_7_days",
        "this_month",
        "last_month",
    }

    APPOINTMENT_STATUSES = (
        Appointment.STATUS_BOOKED,
        Appointment.STATUS_ARRIVED,
        Appointment.STATUS_COMPLETED,
        Appointment.STATUS_CANCELLED,
        Appointment.STATUS_RESCHEDULED,
        Appointment.STATUS_NO_SHOW,
    )

    JOURNEY_TYPES = (
        ("pregnancy", "Pregnancy"),
        ("gynecology", "Gynecology"),
        ("infertility", "Infertility"),
    )

    @staticmethod
    def _parse_date(value):
        if not value:
            return None

        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def resolve_period(
        cls,
        date_from_value=None,
        date_to_value=None,
        preset=None,
    ):
        today = date.today()

        valid_preset = (
            preset
            if preset in cls.PRESETS
            else None
        )

        if valid_preset == "today":
            date_from = today
            date_to = today

        elif valid_preset == "last_7_days":
            date_from = today - timedelta(days=6)
            date_to = today

        elif valid_preset == "last_month":
            current_month_start = today.replace(day=1)
            date_to = current_month_start - timedelta(days=1)
            date_from = date_to.replace(day=1)

        elif valid_preset == "this_month":
            date_from = today.replace(day=1)
            date_to = today

        else:
            date_from = cls._parse_date(
                date_from_value
            )
            date_to = cls._parse_date(
                date_to_value
            )

            if date_from is None or date_to is None:
                date_from = today.replace(day=1)
                date_to = today
                valid_preset = "this_month"
            else:
                valid_preset = "custom"

        was_invalid = date_from > date_to

        if was_invalid:
            date_from = today.replace(day=1)
            date_to = today
            valid_preset = "this_month"

        return {
            "date_from": date_from,
            "date_to": date_to,
            "preset": valid_preset or "this_month",
            "was_invalid": was_invalid,
        }

    @staticmethod
    def _datetime_bounds(date_from, date_to):
        start = datetime.combine(
            date_from,
            time.min,
            tzinfo=timezone.utc,
        )

        end = datetime.combine(
            date_to + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )

        return start, end

    @staticmethod
    def _date_sequence(date_from, date_to):
        days = []
        current = date_from

        while current <= date_to:
            days.append(current)
            current += timedelta(days=1)

        return days

    @staticmethod
    def _normalize_grouped_rows(rows):
        result = {}

        for raw_day, count in rows:
            if isinstance(raw_day, str):
                key = raw_day
            else:
                key = raw_day.isoformat()

            result[key] = int(count)

        return result

    @classmethod
    def get_clinic_kpis(
        cls,
        date_from,
        date_to,
        *,
        include_patients=False,
        include_visits=False,
        include_appointments=False,
    ):
        start, end = cls._datetime_bounds(
            date_from,
            date_to,
        )

        result = {
            "active_patients": None,
            "new_patients": None,
            "visits": None,
            "appointments": None,
        }

        if include_patients:
            result["active_patients"] = (
                Patient.query.filter_by(
                    is_active=True
                ).count()
            )

            result["new_patients"] = (
                Patient.query.filter(
                    Patient.created_at >= start,
                    Patient.created_at < end,
                ).count()
            )

        if include_visits:
            result["visits"] = (
                Visit.query.filter(
                    Visit.visit_date >= start,
                    Visit.visit_date < end,
                ).count()
            )

        if include_appointments:
            result["appointments"] = (
                Appointment.query.filter(
                    Appointment.appointment_date
                    >= date_from,
                    Appointment.appointment_date
                    <= date_to,
                ).count()
            )

        return result

    @classmethod
    def get_activity_trend(
        cls,
        date_from,
        date_to,
        *,
        include_patients=False,
        include_visits=False,
        include_appointments=False,
    ):
        start, end = cls._datetime_bounds(
            date_from,
            date_to,
        )

        days = cls._date_sequence(
            date_from,
            date_to,
        )

        result = {
            "labels": [
                day.strftime("%d %b")
                for day in days
            ],
        }

        if include_patients:
            patient_rows = (
                Patient.query.with_entities(
                    func.date(Patient.created_at),
                    func.count(Patient.id),
                )
                .filter(
                    Patient.created_at >= start,
                    Patient.created_at < end,
                )
                .group_by(
                    func.date(Patient.created_at)
                )
                .all()
            )

            patient_counts = (
                cls._normalize_grouped_rows(
                    patient_rows
                )
            )

            result["new_patients"] = [
                patient_counts.get(
                    day.isoformat(),
                    0,
                )
                for day in days
            ]

        if include_visits:
            visit_rows = (
                Visit.query.with_entities(
                    func.date(Visit.visit_date),
                    func.count(Visit.id),
                )
                .filter(
                    Visit.visit_date >= start,
                    Visit.visit_date < end,
                )
                .group_by(
                    func.date(Visit.visit_date)
                )
                .all()
            )

            visit_counts = (
                cls._normalize_grouped_rows(
                    visit_rows
                )
            )

            result["visits"] = [
                visit_counts.get(
                    day.isoformat(),
                    0,
                )
                for day in days
            ]

        if include_appointments:
            appointment_rows = (
                Appointment.query.with_entities(
                    Appointment.appointment_date,
                    func.count(Appointment.id),
                )
                .filter(
                    Appointment.appointment_date
                    >= date_from,
                    Appointment.appointment_date
                    <= date_to,
                )
                .group_by(
                    Appointment.appointment_date
                )
                .all()
            )

            appointment_counts = (
                cls._normalize_grouped_rows(
                    appointment_rows
                )
            )

            result["appointments"] = [
                appointment_counts.get(
                    day.isoformat(),
                    0,
                )
                for day in days
            ]

        return result

    @classmethod
    def get_journey_mix(
        cls,
        date_from,
        date_to,
    ):
        start, end = cls._datetime_bounds(
            date_from,
            date_to,
        )

        active_rows = (
            Journey.query.with_entities(
                Journey.journey_type,
                func.count(Journey.id),
            )
            .filter(
                Journey.status == "active"
            )
            .group_by(
                Journey.journey_type
            )
            .all()
        )

        active_counts = {
            journey_type: int(count)
            for journey_type, count in active_rows
        }

        new_in_period = (
            Journey.query.filter(
                Journey.created_at >= start,
                Journey.created_at < end,
            ).count()
        )

        return {
            "labels": [
                label
                for _, label in cls.JOURNEY_TYPES
            ],
            "values": [
                active_counts.get(
                    journey_type,
                    0,
                )
                for journey_type, _
                in cls.JOURNEY_TYPES
            ],
            "active_total": sum(
                active_counts.values()
            ),
            "new_in_period": new_in_period,
        }

    @classmethod
    def get_appointment_summary(
        cls,
        date_from,
        date_to,
    ):
        status_rows = (
            Appointment.query.with_entities(
                Appointment.status,
                func.count(Appointment.id),
            )
            .filter(
                Appointment.appointment_date
                >= date_from,
                Appointment.appointment_date
                <= date_to,
            )
            .group_by(
                Appointment.status
            )
            .all()
        )

        status_counts = Counter({
            status: int(count)
            for status, count in status_rows
        })

        return {
            "total": sum(
                status_counts.values()
            ),
            "labels": [
                AppointmentService.STATUS_LABELS[
                    status
                ]
                for status
                in cls.APPOINTMENT_STATUSES
            ],
            "values": [
                status_counts.get(
                    status,
                    0,
                )
                for status
                in cls.APPOINTMENT_STATUSES
            ],
        }

    @staticmethod
    def get_finance_summary(
        date_from,
        date_to,
    ):
        summary = (
            FinanceService.get_insights_summary(
                date_from=date_from,
                date_to=date_to,
            )
        )

        daily_rows = list(
            reversed(
                summary["daily_rows"]
            )
        )

        return {
            "revenue": summary[
                "total_collected"
            ],
            "expenses": summary[
                "total_expenses"
            ],
            "net": summary[
                "net_profit"
            ],
            "outstanding": summary[
                "total_remaining"
            ],
            "daily": {
                "labels": [
                    row["date"].strftime(
                        "%d %b"
                    )
                    for row in daily_rows
                ],
                "revenue": [
                    float(
                        row["collected"]
                    )
                    for row in daily_rows
                ],
                "expenses": [
                    float(
                        row["expenses"]
                    )
                    for row in daily_rows
                ],
            },
        }

    @staticmethod
    def get_today_clinic_snapshot():
        counters = (
            AppointmentService
            .get_counters_for_date(
                date.today()
            )
        )

        return {
            "date": date.today(),
            "appointments": counters[
                "total_booked_today"
            ],
            "waiting": counters[
                "arrived"
            ],
            "completed": counters[
                "completed"
            ],
            "no_show": counters[
                "no_show"
            ],
            "emergency": counters[
                "emergency"
            ],
        }
