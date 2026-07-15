import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class Visit(db.Model):
    """Clinical encounter linked to a patient."""

    __tablename__ = "visits"

    VALID_TYPES = {
        "obs",
        "gyn",
        "infertility",
        "oiti",
        "iui",
        "procedure",
        "general",
    }

    VALID_STATUSES = {
        "open",
        "completed",
        "incomplete",
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

    journey_id = db.Column(
        db.Integer,
        db.ForeignKey("journeys.id"),
        nullable=True,
        index=True,
    )

    visit_type = db.Column(db.String(40), nullable=False, index=True, default="general")
    status = db.Column(db.String(40), nullable=False, index=True, default="open")

    visit_date = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        index=True,
        default=lambda: datetime.now(timezone.utc),
    )
    started_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    reopened_at = db.Column(db.DateTime(timezone=True), nullable=True)

    chief_complaint = db.Column(db.Text, nullable=True)
    history = db.Column(db.Text, nullable=True)
    examination = db.Column(db.Text, nullable=True)
    assessment = db.Column(db.Text, nullable=True)
    plan = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.Date, nullable=True)

    billing_service_type = db.Column(db.String(40), nullable=True, index=True)
    fee_amount = db.Column(db.Numeric(12, 2), nullable=True)
    paid_amount = db.Column(db.Numeric(12, 2), nullable=True)
    payment_method = db.Column(db.String(40), nullable=True, index=True)

    is_locked = db.Column(db.Boolean, nullable=False, default=False)

    completed_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    reopened_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

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
            "visits",
            lazy="dynamic",
            cascade="all, delete-orphan",
        ),
    )

    journey = db.relationship(
        "Journey",
        backref=db.backref(
            "visits",
            lazy="dynamic",
        ),
    )

    completed_by_user = db.relationship(
        "User",
        foreign_keys=[completed_by_user_id],
    )
    reopened_by_user = db.relationship(
        "User",
        foreign_keys=[reopened_by_user_id],
    )

    @property
    def is_completed(self):
        return self.status == "completed"

    @property
    def is_open(self):
        return self.status == "open"

    @property
    def is_unassigned_to_journey(self):
        return self.journey_id is None

    def __repr__(self):
        return f"<Visit {self.uuid} patient={self.patient_id} journey={self.journey_id} type={self.visit_type} status={self.status}>"


class VisitAuditLog(db.Model):
    """Minimal audit log for visit workflow actions."""

    __tablename__ = "visit_audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    visit_id = db.Column(
        db.Integer,
        db.ForeignKey("visits.id"),
        nullable=False,
        index=True,
    )
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )
    actor_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    action = db.Column(db.String(80), nullable=False, index=True)
    from_status = db.Column(db.String(40), nullable=True)
    to_status = db.Column(db.String(40), nullable=True)
    message = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    visit = db.relationship(
        "Visit",
        backref=db.backref(
            "audit_logs",
            lazy="dynamic",
            cascade="all, delete-orphan",
        ),
    )
    patient = db.relationship("Patient")
    actor_user = db.relationship("User")

    def __repr__(self):
        return f"<VisitAuditLog visit={self.visit_id} action={self.action}>"
