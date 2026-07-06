from datetime import date, datetime

from app.extensions import db
from app.models import Journey, Patient


class JourneyService:
    """Journey domain service."""

    TYPE_LABELS = {
        "pregnancy": "Pregnancy",
        "gynecology": "Gynecology",
        "infertility": "Infertility",
    }

    STATUS_LABELS = {
        "active": "Active",
        "closed": "Closed",
    }

    OUTCOME_LABELS = {
        "delivered": "Delivered",
        "miscarriage": "Miscarriage",
        "ectopic": "Ectopic",
        "termination": "Termination",
        "referred": "Referred",
        "transferred_care": "Transferred care",
        "lost_to_follow_up": "Lost to follow-up",
        "other": "Other",
        "resolved": "Resolved",
        "improved": "Improved",
        "chronic_follow_up": "Chronic follow-up",
        "surgery_planned": "Surgery planned",
        "surgery_done": "Surgery done",
        "spontaneous_pregnancy": "Spontaneous pregnancy",
        "pregnancy_after_treatment": "Pregnancy after treatment",
        "iui_success": "IUI success",
        "ivf_referred": "IVF/ICSI referred",
        "treatment_stopped": "Treatment stopped",
    }

    @staticmethod
    def parse_flexible_date(value):
        """Accept YYYY, YYYY-MM, or YYYY-MM-DD and normalize to a date."""

        if isinstance(value, date):
            return value, "day"

        cleaned = (value or "").strip()

        if not cleaned:
            raise ValueError("Date is required.")

        try:
            if len(cleaned) == 4 and cleaned.isdigit():
                return date(int(cleaned), 1, 1), "year"

            if len(cleaned) == 7:
                parsed = datetime.strptime(cleaned, "%Y-%m").date()
                return date(parsed.year, parsed.month, 1), "month"

            parsed = datetime.strptime(cleaned, "%Y-%m-%d").date()
            return parsed, "day"

        except ValueError as exc:
            raise ValueError("Date must be YYYY, YYYY-MM, or YYYY-MM-DD.") from exc

    @staticmethod
    def format_flexible_date(value, precision=None):
        if value is None:
            return ""

        if precision == "year":
            return f"{value.year:04d}"

        if precision == "month":
            return f"{value.year:04d}-{value.month:02d}"

        return value.isoformat()

    @staticmethod
    def validate_journey_type(journey_type):
        if journey_type not in Journey.VALID_TYPES:
            raise ValueError(f"Invalid journey type: {journey_type}")

    @staticmethod
    def validate_status(status):
        if status not in Journey.VALID_STATUSES:
            raise ValueError(f"Invalid journey status: {status}")

    @staticmethod
    def get_outcome_choices(journey_type):
        JourneyService.validate_journey_type(journey_type)

        return sorted(Journey.OUTCOMES_BY_TYPE[journey_type])

    @staticmethod
    def validate_outcome_for_type(journey_type, outcome):
        JourneyService.validate_journey_type(journey_type)

        if outcome not in Journey.OUTCOMES_BY_TYPE[journey_type]:
            raise ValueError(f"Invalid outcome '{outcome}' for {journey_type} journey.")

    @staticmethod
    def validate_new_journey(patient, journey_type, exclude_journey_id=None):
        JourneyService.validate_journey_type(journey_type)

        query = Journey.query.filter_by(
            patient_id=patient.id,
            journey_type=journey_type,
            status="active",
        )

        if exclude_journey_id is not None:
            query = query.filter(Journey.id != exclude_journey_id)

        existing_active = query.first()

        if existing_active:
            raise ValueError(f"Patient already has an active {journey_type} journey.")

    @staticmethod
    def create_journey(**data):
        patient = data.get("patient")
        patient_id = data.get("patient_id")

        if patient is None and patient_id:
            patient = db.session.get(Patient, patient_id)

        if patient is None:
            raise ValueError("Journey must belong to a patient.")

        journey_type = data.get("journey_type")
        JourneyService.validate_new_journey(patient, journey_type)

        title = (data.get("title") or "").strip()
        if not title:
            raise ValueError("Journey title is required.")

        start_date, _precision = JourneyService.parse_flexible_date(data.get("start_date"))

        journey = Journey(
            patient_id=patient.id,
            journey_type=journey_type,
            status="active",
            title=title,
            description=data.get("description"),
            start_date=start_date,
        )

        db.session.add(journey)
        db.session.commit()

        return journey

    @staticmethod
    def update_journey(journey, **data):
        if "journey_type" in data and data["journey_type"] != journey.journey_type:
            JourneyService.validate_new_journey(
                journey.patient,
                data["journey_type"],
                exclude_journey_id=journey.id,
            )
            journey.journey_type = data["journey_type"]

        if "title" in data:
            title = (data.get("title") or "").strip()
            if not title:
                raise ValueError("Journey title is required.")
            journey.title = title

        if "description" in data:
            journey.description = data.get("description")

        if "start_date" in data:
            start_date, _precision = JourneyService.parse_flexible_date(data.get("start_date"))
            journey.start_date = start_date

        db.session.commit()

        return journey

    @staticmethod
    def close_journey(journey, outcome, end_date, outcome_note=None):
        if journey.status == "closed":
            return journey

        JourneyService.validate_outcome_for_type(journey.journey_type, outcome)

        parsed_end_date, precision = JourneyService.parse_flexible_date(end_date)

        journey.status = "closed"
        journey.end_date = parsed_end_date
        journey.end_date_precision = precision
        journey.outcome = outcome
        journey.outcome_note = outcome_note

        db.session.commit()

        return journey

    @staticmethod
    def reopen_journey(journey):
        journey.status = "active"
        journey.end_date = None
        journey.end_date_precision = None
        journey.outcome = None
        journey.outcome_note = None

        JourneyService.validate_new_journey(
            journey.patient,
            journey.journey_type,
            exclude_journey_id=journey.id,
        )

        db.session.commit()

        return journey

    @staticmethod
    def get_patient_journeys(patient):
        return (
            Journey.query.filter_by(patient_id=patient.id)
            .order_by(Journey.start_date.desc(), Journey.id.desc())
            .all()
        )

    @staticmethod
    def get_active_journeys(patient):
        return (
            Journey.query.filter_by(patient_id=patient.id, status="active")
            .order_by(Journey.start_date.desc(), Journey.id.desc())
            .all()
        )

    @staticmethod
    def get_latest_journey(patient, journey_type=None):
        query = Journey.query.filter_by(patient_id=patient.id)

        if journey_type:
            query = query.filter_by(journey_type=journey_type)

        return query.order_by(Journey.start_date.desc(), Journey.id.desc()).first()

    @staticmethod
    def get_type_label(journey_type):
        return JourneyService.TYPE_LABELS.get(journey_type, journey_type)

    @staticmethod
    def get_status_label(status):
        return JourneyService.STATUS_LABELS.get(status, status)

    @staticmethod
    def get_outcome_label(outcome):
        return JourneyService.OUTCOME_LABELS.get(outcome, outcome)
