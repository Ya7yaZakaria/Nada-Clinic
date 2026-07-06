import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class Journey(db.Model):
    """Clinical journey/context for a patient."""

    __tablename__ = "journeys"

    VALID_TYPES = {"pregnancy", "gynecology", "infertility"}
    VALID_STATUSES = {"active", "closed"}

    OUTCOMES_BY_TYPE = {
        "pregnancy": {
            "delivered",
            "miscarriage",
            "ectopic",
            "termination",
            "referred",
            "transferred_care",
            "lost_to_follow_up",
            "other",
        },
        "gynecology": {
            "resolved",
            "improved",
            "chronic_follow_up",
            "referred",
            "surgery_planned",
            "surgery_done",
            "lost_to_follow_up",
            "other",
        },
        "infertility": {
            "spontaneous_pregnancy",
            "pregnancy_after_treatment",
            "iui_success",
            "ivf_referred",
            "treatment_stopped",
            "referred",
            "lost_to_follow_up",
            "other",
        },
    }

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    journey_type = db.Column(db.String(40), nullable=False, index=True)
    status = db.Column(db.String(40), nullable=False, index=True, default="active")

    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=True)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    end_date_precision = db.Column(db.String(20), nullable=True)

    outcome = db.Column(db.String(80), nullable=True, index=True)
    outcome_note = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    patient = db.relationship(
        "Patient",
        backref=db.backref(
            "journeys",
            lazy="dynamic",
            cascade="all, delete-orphan",
        ),
    )

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def is_closed(self):
        return self.status == "closed"

    def __repr__(self):
        return f"<Journey {self.uuid} patient={self.patient_id} type={self.journey_type} status={self.status}>"
