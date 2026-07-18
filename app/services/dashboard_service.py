from collections import Counter
from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.models import (
    Appointment, ClinicUltrasoundExam, ExternalUltrasoundRequest,
    FinanceCharge, FinancePayment, InvestigationOrder,
    InvestigationOrderItem, InvestigationResult, Journey, Patient,
    PatientDocument, Prescription, SurgeryCase, Visit,
)
from app.services.appointment_service import AppointmentService
from app.services.finance_service import FinanceService


class DashboardService:
    VISIT_TYPES = (("obs", "Obstetrics"), ("gyn", "Gynecology"), ("infertility", "Infertility"), ("oiti", "OI/TI"), ("iui", "IUI"), ("procedure", "Procedure"), ("general", "General"))
    APPOINTMENT_TYPES = ((Appointment.TYPE_NEW_CONSULTATION, "New consultation"), (Appointment.TYPE_FOLLOW_UP, "Follow-up"), (Appointment.TYPE_EMERGENCY, "Emergency"))
    APPOINTMENT_SOURCES = ((Appointment.SOURCE_PHONE, "Phone"), (Appointment.SOURCE_WHATSAPP, "WhatsApp"), (Appointment.SOURCE_CLINIC, "Clinic"), (Appointment.SOURCE_EMERGENCY_UNSCHEDULED, "Emergency / unscheduled"))
    ULTRASOUND_TYPES = ((ClinicUltrasoundExam.EXAM_TYPE_OBS, "Obstetrics"), (ClinicUltrasoundExam.EXAM_TYPE_GYNE, "Gynecology"), (ClinicUltrasoundExam.EXAM_TYPE_OI_TI, "OI/TI"), (ClinicUltrasoundExam.EXAM_TYPE_OTHER, "Other"))
    SURGERY_STATUSES = ((SurgeryCase.STATUS_SCHEDULED, "Scheduled"), (SurgeryCase.STATUS_COMPLETED, "Completed"), (SurgeryCase.STATUS_CANCELLED, "Cancelled"), (SurgeryCase.STATUS_POSTPONED, "Postponed"))
    FINANCE_SERVICES = ((FinanceCharge.SERVICE_CONSULTATION, "Consultation"), (FinanceCharge.SERVICE_FOLLOW_UP, "Follow-up"), (FinanceCharge.SERVICE_EMERGENCY, "Emergency"), (FinanceCharge.SERVICE_SURGERY, "Surgery"), (FinanceCharge.SERVICE_PROCEDURE, "Procedure"), (FinanceCharge.SERVICE_ULTRASOUND, "Ultrasound"), (FinanceCharge.SERVICE_INVESTIGATION, "Investigation"), (FinanceCharge.SERVICE_OTHER, "Other"))
    PRESETS = {
        "today",
        "last_7_days",
        "this_month",
        "last_month",
    }

    APPOINTMENT_STATUSES = (
        Appointment.STATUS_BOOKED,
        Appointment.STATUS_ARRIVED,
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
        start_local = datetime.combine(
            date_from,
            time.min,
        )

        end_local = datetime.combine(
            date_to + timedelta(days=1),
            time.min,
        )

        return (
            start_local.astimezone(timezone.utc),
            end_local.astimezone(timezone.utc),
        )

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

        type_rows = Appointment.query.with_entities(Appointment.appointment_type, func.count(Appointment.id)).filter(Appointment.appointment_date >= date_from, Appointment.appointment_date <= date_to).group_by(Appointment.appointment_type).all()
        source_rows = Appointment.query.with_entities(Appointment.source, func.count(Appointment.id)).filter(Appointment.appointment_date >= date_from, Appointment.appointment_date <= date_to).group_by(Appointment.source).all()
        type_counts, source_counts = dict(type_rows), dict(source_rows)
        total = sum(status_counts.values())
        rate = lambda status: round((status_counts.get(status, 0) / total) * 100, 1) if total else 0.0

        return {
            "total": total,
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
            "types": {"labels": [label for _, label in cls.APPOINTMENT_TYPES], "values": [int(type_counts.get(key, 0)) for key, _ in cls.APPOINTMENT_TYPES]},
            "sources": {"labels": [label for _, label in cls.APPOINTMENT_SOURCES], "values": [int(source_counts.get(key, 0)) for key, _ in cls.APPOINTMENT_SOURCES]},
            "no_show": int(
                status_counts.get(
                    Appointment.STATUS_NO_SHOW,
                    0,
                )
            ),
            "cancelled": int(
                status_counts.get(
                    Appointment.STATUS_CANCELLED,
                    0,
                )
            ),
            "no_show_rate": rate(
                Appointment.STATUS_NO_SHOW
            ),
            "cancellation_rate": rate(
                Appointment.STATUS_CANCELLED
            ),
        }

    @classmethod
    def get_visit_summary(cls, date_from, date_to):
        start, end = cls._datetime_bounds(date_from, date_to)
        rows = Visit.query.with_entities(Visit.visit_type, Visit.status, func.count(Visit.id)).filter(Visit.visit_date >= start, Visit.visit_date < end).group_by(Visit.visit_type, Visit.status).all()
        type_counts, status_counts = Counter(), Counter()
        for visit_type, status, count in rows:
            type_counts[visit_type] += int(count)
            status_counts[status] += int(count)
        most_common = max(cls.VISIT_TYPES, key=lambda item: type_counts[item[0]]) if type_counts else None
        return {"total": sum(type_counts.values()), "completed": status_counts["completed"], "incomplete": status_counts["incomplete"], "open": status_counts["open"], "most_common": most_common[1] if most_common and type_counts[most_common[0]] else None, "labels": [label for _, label in cls.VISIT_TYPES], "values": [type_counts[key] for key, _ in cls.VISIT_TYPES]}

    @staticmethod
    def get_upcoming_appointments():
        today, current_time = date.today(), datetime.now().time()
        return Appointment.query.options(joinedload(Appointment.patient)).filter(Appointment.status == Appointment.STATUS_BOOKED, (Appointment.appointment_date > today) | ((Appointment.appointment_date == today) & (Appointment.appointment_time.is_(None) | (Appointment.appointment_time >= current_time)))).order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.is_(None), Appointment.appointment_time.asc(), Appointment.id.asc()).limit(5).all()

    @classmethod
    def get_investigation_summary(cls, date_from, date_to):
        start, end = cls._datetime_bounds(date_from, date_to)
        return {
            "orders_in_period": InvestigationOrder.query.filter(InvestigationOrder.created_at >= start, InvestigationOrder.created_at < end).count(),
            "pending_results": InvestigationOrderItem.query.filter(InvestigationOrderItem.status.in_((InvestigationOrderItem.STATUS_ORDERED, InvestigationOrderItem.STATUS_PENDING_RESULT))).count(),
            "awaiting_review": InvestigationResult.query.filter(InvestigationResult.status == InvestigationResult.STATUS_ENTERED, InvestigationResult.status != InvestigationResult.STATUS_CANCELLED, InvestigationResult.reviewed_at.is_(None)).count(),
            "urgent_pending": InvestigationOrder.query.filter(InvestigationOrder.priority == InvestigationOrder.PRIORITY_URGENT, InvestigationOrder.status.notin_((InvestigationOrder.STATUS_RESULTED, InvestigationOrder.STATUS_REVIEWED, InvestigationOrder.STATUS_CANCELLED))).count(),
            "abnormal_noncritical": InvestigationResult.query.filter(InvestigationResult.status != InvestigationResult.STATUS_CANCELLED, InvestigationResult.abnormal_flag.in_((InvestigationResult.FLAG_LOW, InvestigationResult.FLAG_HIGH, InvestigationResult.FLAG_ABNORMAL))).count(),
            "critical": InvestigationResult.query.filter(InvestigationResult.status != InvestigationResult.STATUS_CANCELLED, InvestigationResult.abnormal_flag == InvestigationResult.FLAG_CRITICAL).count(),
        }

    @classmethod
    def get_ultrasound_summary(cls, date_from, date_to):
        start, end = cls._datetime_bounds(date_from, date_to)
        rows = ClinicUltrasoundExam.query.with_entities(ClinicUltrasoundExam.exam_type, func.count(ClinicUltrasoundExam.id)).join(Visit, ClinicUltrasoundExam.visit_id == Visit.id).filter(ClinicUltrasoundExam.is_active.is_(True), Visit.visit_date >= start, Visit.visit_date < end).group_by(ClinicUltrasoundExam.exam_type).all()
        counts = dict(rows)
        values = [int(counts.get(key, 0)) for key, _ in cls.ULTRASOUND_TYPES]
        return {"clinic_exams": sum(values), "labels": [label for _, label in cls.ULTRASOUND_TYPES], "values": values, "external_pending": ExternalUltrasoundRequest.query.filter_by(status=ExternalUltrasoundRequest.STATUS_PENDING).count(), "external_completed": ExternalUltrasoundRequest.query.filter_by(status=ExternalUltrasoundRequest.STATUS_COMPLETED).count()}

    @classmethod
    def get_surgery_summary(cls, date_from, date_to):
        start, end = cls._datetime_bounds(date_from, date_to)
        rows = SurgeryCase.query.with_entities(SurgeryCase.status, func.count(SurgeryCase.id)).filter(SurgeryCase.is_active.is_(True), SurgeryCase.scheduled_at >= start, SurgeryCase.scheduled_at < end).group_by(SurgeryCase.status).all()
        counts = dict(rows)
        values = [int(counts.get(key, 0)) for key, _ in cls.SURGERY_STATUSES]
        urgent = SurgeryCase.query.filter(SurgeryCase.is_active.is_(True), SurgeryCase.scheduled_at >= start, SurgeryCase.scheduled_at < end, SurgeryCase.priority.in_((SurgeryCase.PRIORITY_URGENT, SurgeryCase.PRIORITY_EMERGENCY))).count()
        return {"total": sum(values), "scheduled": int(counts.get(SurgeryCase.STATUS_SCHEDULED, 0)), "completed": int(counts.get(SurgeryCase.STATUS_COMPLETED, 0)), "cancelled": int(counts.get(SurgeryCase.STATUS_CANCELLED, 0)), "postponed": int(counts.get(SurgeryCase.STATUS_POSTPONED, 0)), "urgent_emergency": urgent, "labels": [label for _, label in cls.SURGERY_STATUSES], "values": values}

    @staticmethod
    def get_upcoming_surgeries():
        return SurgeryCase.query.options(joinedload(SurgeryCase.patient)).filter(SurgeryCase.is_active.is_(True), SurgeryCase.status == SurgeryCase.STATUS_SCHEDULED, SurgeryCase.scheduled_at > datetime.now(timezone.utc)).order_by(SurgeryCase.scheduled_at.asc(), SurgeryCase.id.asc()).limit(3).all()

    @classmethod
    def get_module_activity(cls, date_from, date_to, *, include_prescriptions=False, include_documents=False):
        start, end = cls._datetime_bounds(date_from, date_to)
        result = {}
        if include_prescriptions:
            result["prescriptions"] = Prescription.query.filter(Prescription.created_at >= start, Prescription.created_at < end).count()
        if include_documents:
            result["documents"] = PatientDocument.query.filter(PatientDocument.is_active.is_(True), PatientDocument.created_at >= start, PatientDocument.created_at < end).count()
        return result

    @classmethod
    def get_revenue_by_service(cls, date_from, date_to):
        rows = (
            FinancePayment.query.with_entities(
                FinanceCharge.service_type,
                func.coalesce(
                    func.sum(FinancePayment.amount),
                    0,
                ),
            )
            .join(
                FinanceCharge,
                FinancePayment.charge_id
                == FinanceCharge.id,
            )
            .filter(
                FinancePayment.payment_date
                >= date_from,
                FinancePayment.payment_date
                <= date_to,
                FinanceCharge.status
                != FinanceCharge.STATUS_CANCELLED,
            )
            .group_by(
                FinanceCharge.service_type
            )
            .all()
        )
        amounts = dict(rows)
        return {"labels": [label for _, label in cls.FINANCE_SERVICES], "values": [float(amounts.get(key, 0)) for key, _ in cls.FINANCE_SERVICES]}


    @staticmethod
    def build_needs_attention(
        *,
        appointment_summary=None,
        investigation_summary=None,
        ultrasound_summary=None,
        surgery_summary=None,
        finance_summary=None,
    ):
        items = []

        def add_item(
            label,
            value,
            severity,
            icon,
            endpoint,
            *,
            is_money=False,
        ):
            if value:
                items.append(
                    {
                        "label": label,
                        "value": value,
                        "severity": severity,
                        "icon": icon,
                        "endpoint": endpoint,
                        "is_money": is_money,
                    }
                )

        if appointment_summary:
            add_item(
                "No-show appointments",
                appointment_summary["no_show"],
                "warning",
                "bi-person-x",
                "appointments.index",
            )

        if investigation_summary:
            add_item(
                "Critical investigation results",
                investigation_summary["critical"],
                "danger",
                "bi-exclamation-octagon",
                "investigations.pending_results",
            )
            add_item(
                "Results awaiting review",
                investigation_summary[
                    "awaiting_review"
                ],
                "warning",
                "bi-clipboard2-pulse",
                "investigations.pending_results",
            )
            add_item(
                "Urgent pending investigations",
                investigation_summary[
                    "urgent_pending"
                ],
                "danger",
                "bi-hourglass-split",
                "investigations.index",
            )

        if ultrasound_summary:
            add_item(
                "Pending external ultrasounds",
                ultrasound_summary[
                    "external_pending"
                ],
                "warning",
                "bi-soundwave",
                "patients.index",
            )

        if surgery_summary:
            add_item(
                "Postponed surgeries",
                surgery_summary["postponed"],
                "warning",
                "bi-calendar2-x",
                "surgeries.index",
            )

        if finance_summary:
            add_item(
                "Outstanding balance",
                finance_summary["outstanding"],
                "warning",
                "bi-cash-stack",
                "finance.insights",
                is_money=True,
            )

        return items

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
            "completed": Visit.query.filter(
                Visit.status == "completed",
                Visit.visit_date >= datetime.combine(date.today(), time.min, tzinfo=timezone.utc),
                Visit.visit_date < datetime.combine(date.today() + timedelta(days=1), time.min, tzinfo=timezone.utc),
            ).count(),
            "no_show": counters[
                "no_show"
            ],
            "emergency": counters[
                "emergency"
            ],
        }
