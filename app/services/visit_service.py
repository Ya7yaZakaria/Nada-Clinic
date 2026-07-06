from datetime import datetime, timezone

from app.extensions import db
from app.models import Journey, Patient, Visit, VisitAuditLog


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
    def validate_journey_belongs_to_same_patient(patient, journey):
        if journey is None:
            return

        if journey.patient_id != patient.id:
            raise ValueError("Journey belongs to another patient.")

    @staticmethod
    def create_visit(**data):
        VisitService.validate_visit_data(data)

        patient = data.get("patient")
        patient_id = data.get("patient_id")

        if patient is None:
            patient = db.session.get(Patient, patient_id)

        if patient is None:
            raise ValueError("Patient not found.")

        journey = data.get("journey")
        journey_id = data.get("journey_id")

        if journey is None and journey_id:
            journey = db.session.get(Journey, journey_id)

        if journey_id and journey is None:
            raise ValueError("Journey not found.")

        VisitService.validate_journey_belongs_to_same_patient(patient, journey)

        visit = Visit(
            patient_id=patient.id,
            journey_id=journey.id if journey is not None else None,
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

        if "journey_id" in data:
            VisitService.assign_journey(visit, data["journey_id"], commit=False)

        db.session.commit()

        return visit

    @staticmethod
    def assign_journey(visit, journey_or_id, commit=True):
        if visit.is_locked:
            raise ValueError("Completed visit is locked. Reopen it before changing Journey.")

        if journey_or_id in (None, "", 0, "0"):
            visit.journey_id = None
            if commit:
                db.session.commit()
            return visit

        if isinstance(journey_or_id, Journey):
            journey = journey_or_id
        else:
            journey = db.session.get(Journey, int(journey_or_id))

        if journey is None:
            raise ValueError("Journey not found.")

        VisitService.validate_journey_belongs_to_same_patient(visit.patient, journey)

        visit.journey_id = journey.id

        if commit:
            db.session.commit()

        return visit

    @staticmethod
    def remove_journey(visit):
        return VisitService.assign_journey(visit, None)

    @staticmethod
    def get_available_journeys(patient, include_closed=True):
        query = Journey.query.filter_by(patient_id=patient.id)

        if not include_closed:
            query = query.filter_by(status="active")

        return query.order_by(Journey.status.asc(), Journey.start_date.desc(), Journey.id.desc()).all()

    @staticmethod
    def has_unassigned_journey(visit):
        return visit.journey_id is None

    @staticmethod
    def has_unassigned_warning(visit):
        return VisitService.has_unassigned_journey(visit)

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
    def get_visit_type_label(visit_type):
        return VisitService.TYPE_LABELS.get(visit_type, visit_type)

    @staticmethod
    def get_status_label(status):
        return VisitService.STATUS_LABELS.get(status, status)
