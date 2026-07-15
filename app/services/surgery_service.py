from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from app.extensions import db
from app.models.surgery import SurgeryCase


class SurgeryService:
    """Service layer for operational surgery workflow."""

    CATEGORY_LABELS = {
        SurgeryCase.CATEGORY_CESAREAN_SECTION: "Cesarean section",
        SurgeryCase.CATEGORY_HYSTEROSCOPY: "Hysteroscopy",
        SurgeryCase.CATEGORY_LAPAROSCOPY: "Laparoscopy",
        SurgeryCase.CATEGORY_LAPAROTOMY: "Laparotomy",
        SurgeryCase.CATEGORY_D_AND_C: "D&C",
        SurgeryCase.CATEGORY_MINOR_PROCEDURE: "Minor procedure",
        SurgeryCase.CATEGORY_VAGINAL_SURGERY: "Vaginal surgery",
        SurgeryCase.CATEGORY_OTHER: "Other",
    }

    STATUS_LABELS = {
        SurgeryCase.STATUS_SCHEDULED: "Scheduled",
        SurgeryCase.STATUS_COMPLETED: "Completed",
        SurgeryCase.STATUS_CANCELLED: "Cancelled",
        SurgeryCase.STATUS_POSTPONED: "Postponed",
    }

    PRIORITY_LABELS = {
        SurgeryCase.PRIORITY_ROUTINE: "Routine",
        SurgeryCase.PRIORITY_URGENT: "Urgent",
        SurgeryCase.PRIORITY_EMERGENCY: "Emergency",
    }

    PAYMENT_LABELS = {
        SurgeryCase.PAYMENT_NOT_RECORDED: "Not recorded",
        SurgeryCase.PAYMENT_UNPAID: "Unpaid",
        SurgeryCase.PAYMENT_PARTIAL: "Partial",
        SurgeryCase.PAYMENT_PAID: "Paid",
    }

    @staticmethod
    def get_category_label(value):
        return SurgeryService.CATEGORY_LABELS.get(value, value or "—")

    @staticmethod
    def get_status_label(value):
        return SurgeryService.STATUS_LABELS.get(value, value or "—")

    @staticmethod
    def get_priority_label(value):
        return SurgeryService.PRIORITY_LABELS.get(value, value or "—")

    @staticmethod
    def get_payment_label(value):
        return SurgeryService.PAYMENT_LABELS.get(value, value or "—")

    @staticmethod
    def category_choices():
        return list(SurgeryService.CATEGORY_LABELS.items())

    @staticmethod
    def status_choices():
        return list(SurgeryService.STATUS_LABELS.items())

    @staticmethod
    def priority_choices():
        return list(SurgeryService.PRIORITY_LABELS.items())

    @staticmethod
    def payment_choices():
        return list(SurgeryService.PAYMENT_LABELS.items())

    @staticmethod
    def normalize_money(value):
        if value in ("", None):
            return None
        return Decimal(str(value))

    @staticmethod
    def validate_required(patient, procedure_name, procedure_category, scheduled_at, priority):
        if not patient:
            raise ValueError("Patient is required.")
        if not (procedure_name or "").strip():
            raise ValueError("Procedure name is required.")
        if procedure_category not in SurgeryCase.VALID_CATEGORIES:
            raise ValueError("Invalid surgery category.")
        if not scheduled_at:
            raise ValueError("Scheduled date/time is required.")
        if priority not in SurgeryCase.VALID_PRIORITIES:
            raise ValueError("Invalid surgery priority.")

    @staticmethod
    def validate_payment_status(payment_status):
        if payment_status in ("", None):
            return None
        if payment_status not in SurgeryCase.VALID_PAYMENT_STATUSES:
            raise ValueError("Invalid payment status.")
        return payment_status

    @staticmethod
    def create_surgery(
        *,
        patient,
        procedure_name,
        procedure_category,
        scheduled_at,
        location=None,
        doctor=None,
        priority=SurgeryCase.PRIORITY_ROUTINE,
        pre_op_note=None,
        surgery_note=None,
        source_visit=None,
        fee_amount=None,
        paid_amount=None,
        payment_status=None,
        actor_user=None,
    ):
        SurgeryService.validate_required(
            patient=patient,
            procedure_name=procedure_name,
            procedure_category=procedure_category,
            scheduled_at=scheduled_at,
            priority=priority,
        )

        payment_status = SurgeryService.validate_payment_status(payment_status)

        surgery = SurgeryCase(
            patient=patient,
            source_visit=source_visit,
            procedure_name=procedure_name.strip(),
            procedure_category=procedure_category,
            scheduled_at=scheduled_at,
            location=(location or "").strip() or None,
            doctor=doctor,
            priority=priority,
            pre_op_note=(pre_op_note or "").strip() or None,
            surgery_note=(surgery_note or "").strip() or None,
            fee_amount=SurgeryService.normalize_money(fee_amount),
            paid_amount=SurgeryService.normalize_money(paid_amount),
            payment_status=payment_status,
            status=SurgeryCase.STATUS_SCHEDULED,
            created_by_user=actor_user,
        )
        db.session.add(surgery)
        db.session.commit()
        return surgery

    @staticmethod
    def get_surgery(surgery_uuid):
        if not surgery_uuid:
            return None
        return SurgeryCase.query.filter_by(uuid=surgery_uuid, is_active=True).first()

    @staticmethod
    def update_surgery(
        surgery,
        *,
        procedure_name,
        procedure_category,
        scheduled_at,
        location=None,
        doctor=None,
        priority=SurgeryCase.PRIORITY_ROUTINE,
        pre_op_note=None,
        surgery_note=None,
        fee_amount=None,
        paid_amount=None,
        payment_status=None,
    ):
        if surgery.status == SurgeryCase.STATUS_CANCELLED:
            raise ValueError("Cancelled surgery cannot be edited.")

        SurgeryService.validate_required(
            patient=surgery.patient,
            procedure_name=procedure_name,
            procedure_category=procedure_category,
            scheduled_at=scheduled_at,
            priority=priority,
        )

        surgery.procedure_name = procedure_name.strip()
        surgery.procedure_category = procedure_category
        surgery.scheduled_at = scheduled_at
        surgery.location = (location or "").strip() or None
        surgery.doctor = doctor
        surgery.priority = priority
        surgery.pre_op_note = (pre_op_note or "").strip() or None
        surgery.surgery_note = (surgery_note or "").strip() or None
        surgery.fee_amount = SurgeryService.normalize_money(fee_amount)
        surgery.paid_amount = SurgeryService.normalize_money(paid_amount)
        surgery.payment_status = SurgeryService.validate_payment_status(payment_status)
        db.session.commit()
        return surgery

    @staticmethod
    def complete_surgery(
        surgery,
        *,
        completed_at,
        operative_findings=None,
        operative_details=None,
        complications=None,
        post_op_plan=None,
        fee_amount=None,
        paid_amount=None,
        payment_status=None,
        actor_user=None,
    ):
        if surgery.status not in {SurgeryCase.STATUS_SCHEDULED, SurgeryCase.STATUS_POSTPONED}:
            raise ValueError("Only scheduled or postponed surgery can be completed.")
        if not completed_at:
            raise ValueError("Completion date/time is required.")

        surgery.status = SurgeryCase.STATUS_COMPLETED
        surgery.completed_at = completed_at
        surgery.operative_findings = (operative_findings or "").strip() or None
        surgery.operative_details = (operative_details or "").strip() or None
        surgery.complications = (complications or "").strip() or None
        surgery.post_op_plan = (post_op_plan or "").strip() or None
        surgery.fee_amount = SurgeryService.normalize_money(fee_amount) if fee_amount not in ("", None) else surgery.fee_amount
        surgery.paid_amount = SurgeryService.normalize_money(paid_amount) if paid_amount not in ("", None) else surgery.paid_amount
        if payment_status not in ("", None):
            surgery.payment_status = SurgeryService.validate_payment_status(payment_status)
        surgery.completed_by_user = actor_user
        db.session.commit()
        return surgery

    @staticmethod
    def cancel_surgery(surgery, *, cancel_reason, actor_user=None):
        if surgery.status == SurgeryCase.STATUS_COMPLETED:
            raise ValueError("Completed surgery cannot be cancelled.")
        if surgery.status == SurgeryCase.STATUS_CANCELLED:
            raise ValueError("Surgery is already cancelled.")
        if not (cancel_reason or "").strip():
            raise ValueError("Cancel reason is required.")

        surgery.status = SurgeryCase.STATUS_CANCELLED
        surgery.cancel_reason = cancel_reason.strip()
        surgery.cancelled_at = datetime.now(timezone.utc)
        surgery.cancelled_by_user = actor_user
        db.session.commit()
        return surgery

    @staticmethod
    def postpone_surgery(surgery, *, new_scheduled_at, postponed_reason, actor_user=None):
        if surgery.status == SurgeryCase.STATUS_COMPLETED:
            raise ValueError("Completed surgery cannot be postponed.")
        if surgery.status == SurgeryCase.STATUS_CANCELLED:
            raise ValueError("Cancelled surgery cannot be postponed.")
        if not new_scheduled_at:
            raise ValueError("New scheduled date/time is required.")
        if not (postponed_reason or "").strip():
            raise ValueError("Postponed reason is required.")

        surgery.status = SurgeryCase.STATUS_POSTPONED
        surgery.rescheduled_from_at = surgery.scheduled_at
        surgery.scheduled_at = new_scheduled_at
        surgery.postponed_reason = postponed_reason.strip()
        surgery.postponed_at = datetime.now(timezone.utc)
        surgery.postponed_by_user = actor_user
        db.session.commit()
        return surgery

    @staticmethod
    def mark_postponed_as_scheduled(surgery):
        if surgery.status != SurgeryCase.STATUS_POSTPONED:
            raise ValueError("Only postponed surgery can be marked scheduled.")
        surgery.status = SurgeryCase.STATUS_SCHEDULED
        db.session.commit()
        return surgery

    @staticmethod
    def base_query():
        return SurgeryCase.query.filter_by(is_active=True)

    @staticmethod
    def list_patient_surgeries(patient, limit=None):
        query = (
            SurgeryService.base_query()
            .filter_by(patient_id=patient.id)
            .order_by(SurgeryCase.scheduled_at.desc(), SurgeryCase.id.desc())
        )
        return query.limit(limit).all() if limit else query.all()

    @staticmethod
    def list_source_visit_surgeries(visit):
        return (
            SurgeryService.base_query()
            .filter_by(source_visit_id=visit.id)
            .order_by(SurgeryCase.scheduled_at.desc(), SurgeryCase.id.desc())
            .all()
        )

    @staticmethod
    def list_today_surgeries(today=None):
        today = today or date.today()
        start = datetime.combine(today, time.min).replace(tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        return (
            SurgeryService.base_query()
            .filter(SurgeryCase.scheduled_at >= start)
            .filter(SurgeryCase.scheduled_at < end)
            .order_by(SurgeryCase.scheduled_at.asc(), SurgeryCase.id.asc())
            .all()
        )

    @staticmethod
    def list_upcoming_surgeries(limit=10):
        now = datetime.now(timezone.utc)
        return (
            SurgeryService.base_query()
            .filter(SurgeryCase.scheduled_at >= now)
            .filter(SurgeryCase.status.in_([SurgeryCase.STATUS_SCHEDULED, SurgeryCase.STATUS_POSTPONED]))
            .order_by(SurgeryCase.scheduled_at.asc(), SurgeryCase.id.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def list_recent_completed(limit=10):
        return (
            SurgeryService.base_query()
            .filter_by(status=SurgeryCase.STATUS_COMPLETED)
            .order_by(SurgeryCase.completed_at.desc(), SurgeryCase.id.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def list_by_statuses(statuses, limit=10):
        return (
            SurgeryService.base_query()
            .filter(SurgeryCase.status.in_(statuses))
            .order_by(SurgeryCase.scheduled_at.desc(), SurgeryCase.id.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def list_by_date_range(date_from=None, date_to=None, status=None, category=None, patient_query=None):
        query = SurgeryService.base_query()

        if date_from:
            query = query.filter(SurgeryCase.scheduled_at >= datetime.combine(date_from, time.min).replace(tzinfo=timezone.utc))
        if date_to:
            query = query.filter(SurgeryCase.scheduled_at <= datetime.combine(date_to, time.max).replace(tzinfo=timezone.utc))
        if status:
            query = query.filter(SurgeryCase.status == status)
        if category:
            query = query.filter(SurgeryCase.procedure_category == category)
        if patient_query:
            from app.models.patient import Patient
            like = f"%{patient_query.strip()}%"
            query = query.join(Patient).filter(
                (Patient.name_ar.ilike(like)) |
                (Patient.name_en.ilike(like)) |
                (Patient.phone_primary.ilike(like))
            )

        return query.order_by(SurgeryCase.scheduled_at.desc(), SurgeryCase.id.desc()).all()
