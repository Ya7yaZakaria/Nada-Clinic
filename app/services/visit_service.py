from datetime import datetime, timezone

from app.extensions import db
from app.models import Patient, Visit, VisitAuditLog


class VisitService:
    """Visit domain service."""

    TYPE_LABELS = {
        "obs": "OBS",
        "gyn": "Gyn",
        "infertility": "Infertility",
        "oiti": "OITI",
        "iui": "IUI",
        "procedure": "Procedure",
        "general": "General",
    }

    STATUS_LABELS = {
        "open": "Open",
        "completed": "Completed",
        "incomplete": "Incomplete",
    }

    @staticmethod
    def validate_visit_data(data):
        patient = data.get("patient")
        patient_id = data.get("patient_id")

        if not patient and not patient_id:
            raise ValueError("Visit must belong to a patient.")

        visit_type = data.get("visit_type") or "general"
        if visit_type not in Visit.VALID_TYPES:
            raise ValueError(f"Invalid visit type: {visit_type}")

        status = data.get("status") or "open"
        if status not in Visit.VALID_STATUSES:
            raise ValueError(f"Invalid visit status: {status}")

    @staticmethod
    def create_visit(**data):
        VisitService.validate_visit_data(data)

        patient = data.get("patient")
        patient_id = data.get("patient_id")

        if patient is None:
            patient = db.session.get(Patient, patient_id)

        if patient is None:
            raise ValueError("Patient not found.")

        visit = Visit(
            patient_id=patient.id,
            visit_type=data.get("visit_type") or "general",
            status=data.get("status") or "open",
            visit_date=data.get("visit_date") or datetime.now(timezone.utc),
            started_at=data.get("started_at") or datetime.now(timezone.utc),
            chief_complaint=data.get("chief_complaint"),
            history=data.get("history"),
            examination=data.get("examination"),
            assessment=data.get("assessment"),
            plan=data.get("plan"),
            follow_up_date=data.get("follow_up_date"),
            is_locked=bool(data.get("is_locked", False)),
        )

        db.session.add(visit)
        db.session.commit()

        return visit

    @staticmethod
    def update_visit(visit, **data):
        if visit.is_locked:
            raise ValueError("Completed visit is locked. Reopen it before editing.")

        allowed_fields = [
            "visit_type",
            "status",
            "visit_date",
            "chief_complaint",
            "history",
            "examination",
            "assessment",
            "plan",
            "follow_up_date",
        ]

        candidate = {
            "patient_id": visit.patient_id,
            "visit_type": data.get("visit_type", visit.visit_type),
            "status": data.get("status", visit.status),
        }
        VisitService.validate_visit_data(candidate)

        for field in allowed_fields:
            if field in data:
                setattr(visit, field, data[field])

        db.session.commit()

        return visit

    @staticmethod
    def complete_visit(visit, actor_user=None, confirmed=False):
        if not confirmed:
            raise ValueError("Visit completion must be confirmed.")

        if visit.status == "completed":
            return visit

        previous_status = visit.status
        now = datetime.now(timezone.utc)

        visit.status = "completed"
        visit.is_locked = True
        visit.completed_at = now

        if actor_user is not None:
            visit.completed_by_user_id = actor_user.id

        VisitService.create_audit_log(
            visit=visit,
            actor_user=actor_user,
            action="visit.completed",
            from_status=previous_status,
            to_status="completed",
            message="Visit completed with confirmation.",
            commit=False,
        )

        db.session.commit()

        return visit

    @staticmethod
    def reopen_visit(visit, actor_user=None, confirmed=False):
        if not confirmed:
            raise ValueError("Visit reopen must be confirmed.")

        if actor_user is not None and not VisitService.can_reopen_visit(actor_user):
            raise PermissionError("Only Doctor/Admin can reopen a completed visit.")

        if visit.status != "completed":
            return visit

        previous_status = visit.status
        now = datetime.now(timezone.utc)

        visit.status = "open"
        visit.is_locked = False
        visit.reopened_at = now

        if actor_user is not None:
            visit.reopened_by_user_id = actor_user.id

        VisitService.create_audit_log(
            visit=visit,
            actor_user=actor_user,
            action="visit.reopened",
            from_status=previous_status,
            to_status="open",
            message="Visit reopened with confirmation.",
            commit=False,
        )

        db.session.commit()

        return visit

    @staticmethod
    def can_reopen_visit(user):
        if user is None:
            return False

        return user.has_role("Admin") or user.has_role("Doctor")

    @staticmethod
    def create_audit_log(
        visit,
        actor_user=None,
        action=None,
        from_status=None,
        to_status=None,
        message=None,
        commit=True,
    ):
        audit_log = VisitAuditLog(
            visit_id=visit.id,
            patient_id=visit.patient_id,
            actor_user_id=actor_user.id if actor_user is not None else None,
            action=action,
            from_status=from_status,
            to_status=to_status,
            message=message,
        )

        db.session.add(audit_log)

        if commit:
            db.session.commit()

        return audit_log

    @staticmethod
    def get_patient_visits(patient, limit=20):
        return (
            Visit.query.filter_by(patient_id=patient.id)
            .order_by(Visit.visit_date.desc(), Visit.id.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_last_visit(patient):
        return (
            Visit.query.filter_by(patient_id=patient.id)
            .order_by(Visit.visit_date.desc(), Visit.id.desc())
            .first()
        )

    @staticmethod
    def has_unassigned_journey(visit):
        return True

    @staticmethod
    def get_visit_type_label(visit_type):
        return VisitService.TYPE_LABELS.get(visit_type, visit_type)

    @staticmethod
    def get_status_label(status):
        return VisitService.STATUS_LABELS.get(status, status)
