from calendar import month_abbr
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from math import ceil

from app.extensions import db
from app.models import Appointment, FinanceCharge, InvestigationResult, Journey, Patient, Visit


@dataclass
class PatientDirectoryPage:
    items: list
    page: int
    per_page: int
    total: int

    @property
    def pages(self):
        return max(1, ceil(self.total / self.per_page))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def next_num(self):
        return self.page + 1


@dataclass
class PatientDirectoryRow:
    patient: Patient
    last_visit: Visit | None = None
    next_appointment: Appointment | None = None
    active_journey: Journey | None = None
    first_pending_result: InvestigationResult | None = None
    pending_result_count: int = 0
    outstanding_balance: Decimal = Decimal("0.00")

    @property
    def last_visit_at(self):
        return self.last_visit.visit_date if self.last_visit else None


class PatientDashboardService:
    """Permission-aware, read-only queries for the Patients command center."""

    DEFAULT_PER_PAGE = 20
    MAX_PER_PAGE = 50
    VALID_PERIODS = {"30d", "6m", "12m"}
    VALID_DRAWER_SORTS = {"urgent", "recently_seen", "nearest", "name", "balance", "newest"}

    @staticmethod
    def _month_start(value):
        return value.replace(day=1)

    @staticmethod
    def _shift_month(value, offset):
        month_index = value.year * 12 + value.month - 1 + offset
        return date(month_index // 12, month_index % 12 + 1, 1)

    @staticmethod
    def _last_visit_subquery():
        return (
            db.select(db.func.max(Visit.visit_date))
            .where(Visit.patient_id == Patient.id)
            .correlate(Patient)
            .scalar_subquery()
        )

    @staticmethod
    def _next_appointment_subquery():
        return (
            db.select(db.func.min(Appointment.appointment_date))
            .where(
                Appointment.patient_id == Patient.id,
                Appointment.appointment_date >= date.today(),
                Appointment.status.in_([Appointment.STATUS_BOOKED, Appointment.STATUS_ARRIVED]),
            )
            .correlate(Patient)
            .scalar_subquery()
        )

    @staticmethod
    def _pending_count_subquery():
        return (
            db.select(db.func.count(InvestigationResult.id))
            .where(
                InvestigationResult.patient_id == Patient.id,
                InvestigationResult.status == InvestigationResult.STATUS_ENTERED,
            )
            .correlate(Patient)
            .scalar_subquery()
        )

    @staticmethod
    def _balance_subquery():
        return (
            db.select(db.func.coalesce(db.func.sum(FinanceCharge.remaining_amount), 0))
            .where(
                FinanceCharge.patient_id == Patient.id,
                FinanceCharge.status.in_([FinanceCharge.STATUS_UNPAID, FinanceCharge.STATUS_PARTIAL]),
            )
            .correlate(Patient)
            .scalar_subquery()
        )

    @staticmethod
    def _matches_search(query):
        cleaned = (query or "").strip()
        if not cleaned:
            return None
        normalized_phone = cleaned.replace(" ", "").replace("-", "")
        filters = [
            Patient.name_ar.ilike(f"%{cleaned}%"),
            Patient.name_en.ilike(f"%{cleaned}%"),
            Patient.search_name.ilike(f"%{cleaned.lower()}%"),
            Patient.phone_primary.ilike(f"%{normalized_phone}%"),
            Patient.phone_secondary.ilike(f"%{normalized_phone}%"),
        ]
        if cleaned.isdigit():
            filters.append(Patient.medical_file_number == int(cleaned))
        return db.or_(*filters)

    @staticmethod
    def _period_days(period):
        return {"30d": 30, "6m": 183, "12m": 365}.get(period, 183)

    @staticmethod
    def list_patients(
        *, q="", status="active", journey="all", last_seen="any", upcoming=False,
        pending_results=False, outstanding=False, cohort=None, segment=None, period="6m",
        sort="recently_seen", page=1, per_page=DEFAULT_PER_PAGE,
        can_view_clinical=False, can_view_finance=False,
    ):
        page = max(1, int(page or 1))
        per_page = min(PatientDashboardService.MAX_PER_PAGE, max(1, int(per_page or 20)))
        period = period if period in PatientDashboardService.VALID_PERIODS else "6m"
        today = date.today()
        last_visit = PatientDashboardService._last_visit_subquery()
        next_appointment = PatientDashboardService._next_appointment_subquery()
        pending_count = PatientDashboardService._pending_count_subquery()
        balance = PatientDashboardService._balance_subquery()
        patient_query = Patient.query

        search_filter = PatientDashboardService._matches_search(q)
        if search_filter is not None:
            patient_query = patient_query.filter(search_filter)

        if status == "inactive":
            patient_query = patient_query.filter(Patient.is_active.is_(False))
        elif status != "all":
            patient_query = patient_query.filter(Patient.is_active.is_(True))

        month_start = datetime.combine(today.replace(day=1), time.min, tzinfo=timezone.utc)
        recent_30 = datetime.combine(today - timedelta(days=30), time.min)
        dormant_cutoff = datetime.combine(today - timedelta(days=183), time.min)
        period_start = datetime.combine(today - timedelta(days=PatientDashboardService._period_days(period)), time.min, tzinfo=timezone.utc)

        if cohort == "new_this_month":
            patient_query = patient_query.filter(Patient.created_at >= month_start)
        elif cohort == "new_period":
            patient_query = patient_query.filter(Patient.created_at >= period_start)
        elif cohort == "returning":
            patient_query = patient_query.filter(
                Patient.created_at < period_start,
                db.exists().where(Visit.patient_id == Patient.id, Visit.visit_date >= period_start),
            )
        elif cohort in {"seen_30_days", "seen_recent"}:
            cutoff = recent_30 if cohort == "seen_30_days" else dormant_cutoff
            patient_query = patient_query.filter(last_visit >= cutoff)
        elif cohort == "dormant":
            patient_query = patient_query.filter(db.or_(last_visit.is_(None), last_visit < dormant_cutoff))
        elif cohort == "never_seen":
            patient_query = patient_query.filter(last_visit.is_(None))
        elif cohort == "follow_up_overdue" and can_view_clinical:
            patient_query = patient_query.filter(
                db.exists().where(Visit.patient_id == Patient.id, Visit.follow_up_date < today)
            )
        elif cohort == "follow_up_upcoming" and can_view_clinical:
            patient_query = patient_query.filter(
                db.exists().where(Visit.patient_id == Patient.id, Visit.follow_up_date >= today)
            )
        elif cohort == "pending_review" and can_view_clinical:
            patient_query = patient_query.filter(pending_count > 0)
        elif cohort == "outstanding" and can_view_finance:
            patient_query = patient_query.filter(balance > 0)
        elif cohort == "attention":
            attention = []
            if can_view_clinical:
                attention.append(pending_count > 0)
            if can_view_finance:
                attention.append(balance > 0)
            patient_query = patient_query.filter(db.or_(*attention) if attention else db.false())

        if cohort == "appointment" and segment:
            valid_statuses = {
                Appointment.STATUS_BOOKED, Appointment.STATUS_ARRIVED, Appointment.STATUS_CANCELLED,
                Appointment.STATUS_RESCHEDULED, Appointment.STATUS_NO_SHOW,
            }
            if segment in valid_statuses:
                patient_query = patient_query.filter(
                    db.exists().where(
                        Appointment.patient_id == Patient.id,
                        Appointment.appointment_date >= period_start.date(),
                        Appointment.status == segment,
                    )
                )

        if cohort == "age" and segment:
            ranges = {"under_25": (0, 24), "25_34": (25, 34), "35_44": (35, 44), "45_plus": (45, 120)}
            if segment in ranges:
                low, high = ranges[segment]
                newest_dob = date(today.year - low, today.month, min(today.day, 28))
                oldest_dob = date(today.year - high - 1, today.month, min(today.day, 28))
                patient_query = patient_query.filter(Patient.date_of_birth > oldest_dob, Patient.date_of_birth <= newest_dob)

        if can_view_clinical and journey in Journey.VALID_TYPES:
            patient_query = patient_query.filter(
                db.exists().where(
                    Journey.patient_id == Patient.id,
                    Journey.status == "active",
                    Journey.journey_type == journey,
                )
            )

        if last_seen == "never":
            patient_query = patient_query.filter(last_visit.is_(None))
        elif last_seen in {"today", "30d", "6m"}:
            days = {"today": 0, "30d": 30, "6m": 183}[last_seen]
            patient_query = patient_query.filter(last_visit >= datetime.combine(today - timedelta(days=days), time.min))

        if upcoming:
            patient_query = patient_query.filter(next_appointment.is_not(None))
        if pending_results and can_view_clinical:
            patient_query = patient_query.filter(pending_count > 0)
        if outstanding and can_view_finance:
            patient_query = patient_query.filter(balance > 0)

        if sort == "newest":
            patient_query = patient_query.order_by(Patient.created_at.desc(), Patient.id.desc())
        elif sort == "name":
            patient_query = patient_query.order_by(Patient.name_en.asc(), Patient.id.asc())
        elif sort == "mrn":
            patient_query = patient_query.order_by(Patient.medical_file_number.asc())
        elif sort == "nearest":
            patient_query = patient_query.order_by(next_appointment.is_(None), next_appointment.asc(), Patient.id.asc())
        elif sort == "balance" and can_view_finance:
            patient_query = patient_query.order_by(balance.desc(), Patient.id.desc())
        elif sort == "urgent":
            urgency = (pending_count if can_view_clinical else db.literal(0)) + (db.case((balance > 0, 1), else_=0) if can_view_finance else db.literal(0))
            patient_query = patient_query.order_by(urgency.desc(), db.func.coalesce(last_visit, Patient.created_at).desc())
        else:
            patient_query = patient_query.order_by(db.func.coalesce(last_visit, Patient.created_at).desc(), Patient.id.desc())

        pagination = patient_query.paginate(page=page, per_page=per_page, error_out=False)
        rows = PatientDashboardService._build_rows(
            pagination.items, can_view_clinical=can_view_clinical, can_view_finance=can_view_finance
        )
        return PatientDirectoryPage(rows, page, per_page, pagination.total)

    @staticmethod
    def _build_rows(patients, *, can_view_clinical, can_view_finance):
        if not patients:
            return []
        patient_ids = [patient.id for patient in patients]
        today = date.today()

        last_visits = {}
        for visit in (
            Visit.query.filter(Visit.patient_id.in_(patient_ids))
            .order_by(Visit.visit_date.desc(), Visit.id.desc()).all()
        ):
            last_visits.setdefault(visit.patient_id, visit)

        next_appointments = {}
        for appointment in (
            Appointment.query.filter(
                Appointment.patient_id.in_(patient_ids), Appointment.appointment_date >= today,
                Appointment.status.in_([Appointment.STATUS_BOOKED, Appointment.STATUS_ARRIVED]),
            ).order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc(), Appointment.id.asc()).all()
        ):
            next_appointments.setdefault(appointment.patient_id, appointment)

        active_journeys, pending_counts, first_pending = {}, {}, {}
        if can_view_clinical:
            for journey in (
                Journey.query.filter(Journey.patient_id.in_(patient_ids), Journey.status == "active")
                .order_by(Journey.start_date.desc(), Journey.id.desc()).all()
            ):
                active_journeys.setdefault(journey.patient_id, journey)
            for result in (
                InvestigationResult.query.filter(
                    InvestigationResult.patient_id.in_(patient_ids),
                    InvestigationResult.status == InvestigationResult.STATUS_ENTERED,
                ).order_by(InvestigationResult.result_date.desc(), InvestigationResult.id.desc()).all()
            ):
                pending_counts[result.patient_id] = pending_counts.get(result.patient_id, 0) + 1
                first_pending.setdefault(result.patient_id, result)

        balances = {}
        if can_view_finance:
            balances = dict(
                db.session.query(FinanceCharge.patient_id, db.func.coalesce(db.func.sum(FinanceCharge.remaining_amount), 0))
                .filter(
                    FinanceCharge.patient_id.in_(patient_ids),
                    FinanceCharge.status.in_([FinanceCharge.STATUS_UNPAID, FinanceCharge.STATUS_PARTIAL]),
                ).group_by(FinanceCharge.patient_id).all()
            )

        return [
            PatientDirectoryRow(
                patient=patient,
                last_visit=last_visits.get(patient.id),
                next_appointment=next_appointments.get(patient.id),
                active_journey=active_journeys.get(patient.id),
                first_pending_result=first_pending.get(patient.id),
                pending_result_count=int(pending_counts.get(patient.id, 0)),
                outstanding_balance=Decimal(balances.get(patient.id, 0)),
            ) for patient in patients
        ]

    @staticmethod
    def get_kpis(*, can_view_clinical=False, can_view_finance=False):
        today = date.today()
        month_start = datetime.combine(today.replace(day=1), time.min, tzinfo=timezone.utc)
        recent_cutoff = datetime.combine(today - timedelta(days=30), time.min)
        attention = []
        if can_view_clinical:
            attention.append(PatientDashboardService._pending_count_subquery() > 0)
        if can_view_finance:
            attention.append(PatientDashboardService._balance_subquery() > 0)
        return {
            "active_patients": Patient.query.filter(Patient.is_active.is_(True)).count(),
            "new_this_month": Patient.query.filter(Patient.created_at >= month_start).count(),
            "seen_last_30_days": db.session.query(db.func.count(db.distinct(Visit.patient_id))).filter(Visit.visit_date >= recent_cutoff).scalar() or 0,
            "need_attention": Patient.query.filter(db.or_(*attention)).count() if attention else 0,
        }

    @staticmethod
    def _chart(key, title, kicker, items, insight, *, restricted=False):
        maximum = max([int(item.get("value", 0)) for item in items] + [1])
        for item in items:
            item["percent"] = max(4 if item.get("value") else 2, round(int(item.get("value", 0)) / maximum * 100))
        return {"key": key, "title": title, "kicker": kicker, "items": items, "insight": insight, "restricted": restricted}

    @staticmethod
    def get_analytics(*, period="6m", can_view_clinical=False, can_view_finance=False):
        period = period if period in PatientDashboardService.VALID_PERIODS else "6m"
        today = date.today()
        days = PatientDashboardService._period_days(period)
        start_date = today - timedelta(days=days)
        start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        previous_start = start_dt - timedelta(days=days)
        charts = []

        bucket_count = 6 if period != "12m" else 12
        if period == "30d":
            width = 5
            buckets = []
            for index in range(bucket_count):
                bucket_start = start_date + timedelta(days=index * width)
                bucket_end = bucket_start + timedelta(days=width)
                count = Patient.query.filter(Patient.created_at >= datetime.combine(bucket_start, time.min, tzinfo=timezone.utc), Patient.created_at < datetime.combine(bucket_end, time.min, tzinfo=timezone.utc)).count()
                buckets.append({"label": bucket_start.strftime("%d %b"), "value": count, "cohort": "new_period"})
        else:
            first_month = PatientDashboardService._shift_month(today.replace(day=1), -(bucket_count - 1))
            buckets = []
            for index in range(bucket_count):
                bucket_start = PatientDashboardService._shift_month(first_month, index)
                bucket_end = PatientDashboardService._shift_month(bucket_start, 1)
                count = Patient.query.filter(Patient.created_at >= datetime.combine(bucket_start, time.min, tzinfo=timezone.utc), Patient.created_at < datetime.combine(bucket_end, time.min, tzinfo=timezone.utc)).count()
                buckets.append({"label": month_abbr[bucket_start.month], "value": count, "cohort": "new_period"})
        current_new = Patient.query.filter(Patient.created_at >= start_dt).count()
        previous_new = Patient.query.filter(Patient.created_at >= previous_start, Patient.created_at < start_dt).count()
        delta = current_new - previous_new
        charts.append(PatientDashboardService._chart("growth", "New registrations", "Patient growth", buckets, f"{current_new} new patients in this period ({delta:+d} vs previous period)."))

        period_visit_ids = {row[0] for row in db.session.query(Visit.patient_id).filter(Visit.visit_date >= start_dt).distinct().all()}
        new_ids = {row[0] for row in db.session.query(Patient.id).filter(Patient.created_at >= start_dt).all()}
        returning = len(period_visit_ids - new_ids)
        charts.append(PatientDashboardService._chart("engagement", "New vs returning", "Engagement", [
            {"label": "New", "value": len(new_ids), "cohort": "new_period"},
            {"label": "Returning", "value": returning, "cohort": "returning"},
        ], f"{returning} established patients returned during the selected period."))

        recent_cutoff = datetime.combine(today - timedelta(days=183), time.min)
        seen_recent = db.session.query(db.func.count(db.distinct(Visit.patient_id))).filter(Visit.visit_date >= recent_cutoff).scalar() or 0
        active_total = Patient.query.filter(Patient.is_active.is_(True)).count()
        dormant = max(0, active_total - seen_recent)
        charts.append(PatientDashboardService._chart("activity", "Seen vs dormant", "Continuity", [
            {"label": "Seen <6m", "value": seen_recent, "cohort": "seen_recent"},
            {"label": "Dormant", "value": dormant, "cohort": "dormant"},
        ], f"{dormant} active patients have not been seen in the last six months."))

        ages = {"under_25": 0, "25_34": 0, "35_44": 0, "45_plus": 0}
        for dob, in Patient.query.with_entities(Patient.date_of_birth).filter(Patient.date_of_birth.is_not(None)).all():
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            key = "under_25" if age < 25 else "25_34" if age < 35 else "35_44" if age < 45 else "45_plus"
            ages[key] += 1
        age_items = [{"label": label, "value": ages[key], "cohort": "age", "segment": key} for key, label in (("under_25", "<25"), ("25_34", "25–34"), ("35_44", "35–44"), ("45_plus", "45+"))]
        largest_age = max(age_items, key=lambda item: item["value"])
        charts.append(PatientDashboardService._chart("ages", "Age distribution", "Population", age_items, f"The largest recorded age group is {largest_age['label']} ({largest_age['value']} patients)."))

        appointment_items = []
        for status, label in (("booked", "Booked"), ("arrived", "Arrived"), ("cancelled", "Cancelled"), ("no_show", "No-show")):
            value = db.session.query(db.func.count(Appointment.id)).filter(Appointment.appointment_date >= start_date, Appointment.status == status).scalar() or 0
            appointment_items.append({"label": label, "value": value, "cohort": "appointment", "segment": status})
        no_shows = next(item["value"] for item in appointment_items if item["label"] == "No-show")
        charts.append(PatientDashboardService._chart("appointments", "Appointment activity", "Operations", appointment_items, f"{no_shows} no-show appointments were recorded in this period."))

        if can_view_clinical:
            journey_items = []
            for kind, label in (("pregnancy", "Pregnancy"), ("infertility", "Infertility"), ("gynecology", "Gynecology")):
                value = db.session.query(db.func.count(db.distinct(Journey.patient_id))).filter(Journey.status == "active", Journey.journey_type == kind).scalar() or 0
                journey_items.append({"label": label, "value": value, "journey": kind})
            total_journeys = sum(item["value"] for item in journey_items)
            leader = max(journey_items, key=lambda item: item["value"])
            charts.append(PatientDashboardService._chart("journeys", "Active care journeys", "Clinical mix", journey_items, f"{leader['label']} is the largest active journey group ({leader['value']} of {total_journeys})."))

            overdue = db.session.query(db.func.count(db.distinct(Visit.patient_id))).filter(Visit.follow_up_date < today).scalar() or 0
            upcoming = db.session.query(db.func.count(db.distinct(Visit.patient_id))).filter(Visit.follow_up_date >= today).scalar() or 0
            charts.append(PatientDashboardService._chart("followups", "Follow-up status", "Clinical workload", [
                {"label": "Overdue", "value": overdue, "cohort": "follow_up_overdue"},
                {"label": "Upcoming", "value": upcoming, "cohort": "follow_up_upcoming"},
            ], f"{overdue} patients have a recorded follow-up date that is now overdue."))

        attention_items = []
        if can_view_clinical:
            pending = db.session.query(db.func.count(db.distinct(InvestigationResult.patient_id))).filter(InvestigationResult.status == InvestigationResult.STATUS_ENTERED).scalar() or 0
            attention_items.append({"label": "Reviews", "value": pending, "cohort": "pending_review"})
        if can_view_finance:
            balances = db.session.query(db.func.count(db.distinct(FinanceCharge.patient_id))).filter(FinanceCharge.status.in_([FinanceCharge.STATUS_UNPAID, FinanceCharge.STATUS_PARTIAL]), FinanceCharge.remaining_amount > 0).scalar() or 0
            attention_items.append({"label": "Balances", "value": balances, "cohort": "outstanding"})
        if attention_items:
            total_attention = sum(item["value"] for item in attention_items)
            charts.append(PatientDashboardService._chart("attention", "Attention categories", "Work queue", attention_items, f"{total_attention} actionable patient indicators are visible to your role."))

        if can_view_finance:
            total_outstanding = db.session.query(db.func.coalesce(db.func.sum(FinanceCharge.remaining_amount), 0)).filter(FinanceCharge.status.in_([FinanceCharge.STATUS_UNPAID, FinanceCharge.STATUS_PARTIAL])).scalar() or 0
            unpaid_patients = db.session.query(db.func.count(db.distinct(FinanceCharge.patient_id))).filter(FinanceCharge.remaining_amount > 0).scalar() or 0
            charts.append(PatientDashboardService._chart("finance", "Patient balances", "Finance", [
                {"label": "Patients due", "value": unpaid_patients, "cohort": "outstanding"},
            ], f"{Decimal(total_outstanding):,.0f} EGP remains outstanding across {unpaid_patients} patients."))

        return {"period": period, "charts": charts}

    @staticmethod
    def get_insights(*, can_view_clinical=False):
        """Compatibility wrapper retained for older callers and tests."""
        analytics = PatientDashboardService.get_analytics(period="6m", can_view_clinical=can_view_clinical)
        growth = next(chart for chart in analytics["charts"] if chart["key"] == "growth")
        journey = next((chart for chart in analytics["charts"] if chart["key"] == "journeys"), None)
        trend = [{"label": item["label"], "count": item["value"], "percent": item["percent"]} for item in growth["items"]]
        care_mix = []
        if journey:
            total = sum(item["value"] for item in journey["items"]) or 1
            care_mix = [{"key": item["journey"], "label": item["label"], "count": item["value"], "percent": round(item["value"] / total * 100)} for item in journey["items"]]
        return {"registration_trend": trend, "care_mix": care_mix}
