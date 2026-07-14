import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class ClinicUltrasoundExam(db.Model):
    """Structured clinic ultrasound done during a Visit."""

    __tablename__ = "clinic_ultrasound_exams"

    EXAM_TYPE_OBS = "obs"
    EXAM_TYPE_GYNE = "gyne"
    EXAM_TYPE_OI_TI = "oi_ti"
    EXAM_TYPE_OTHER = "other"

    EXAM_TYPES = {
        EXAM_TYPE_OBS,
        EXAM_TYPE_GYNE,
        EXAM_TYPE_OI_TI,
        EXAM_TYPE_OTHER,
    }

    ROUTE_TRANSABDOMINAL = "transabdominal"
    ROUTE_TRANSVAGINAL = "transvaginal"
    ROUTE_BOTH = "both"
    ROUTE_UNKNOWN = "unknown"

    EXAM_ROUTES = {
        ROUTE_TRANSABDOMINAL,
        ROUTE_TRANSVAGINAL,
        ROUTE_BOTH,
        ROUTE_UNKNOWN,
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

    visit_id = db.Column(
        db.Integer,
        db.ForeignKey("visits.id"),
        nullable=False,
        index=True,
    )

    journey_id = db.Column(
        db.Integer,
        db.ForeignKey("journeys.id"),
        nullable=True,
        index=True,
    )

    exam_type = db.Column(db.String(40), nullable=False, index=True)
    exam_route = db.Column(db.String(40), nullable=False, default=ROUTE_UNKNOWN, index=True)

    findings_json = db.Column(db.JSON, nullable=False, default=dict)
    findings_text = db.Column(db.Text, nullable=True)
    extra_note = db.Column(db.Text, nullable=True)
    impression = db.Column(db.Text, nullable=True)
    sketch_note = db.Column(db.Text, nullable=True)

    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)

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

    patient = db.relationship("Patient")
    visit = db.relationship(
        "Visit",
        backref=db.backref("clinic_ultrasound_exams", lazy="dynamic"),
    )
    journey = db.relationship("Journey")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])

    @property
    def exam_date(self):
        """Display date comes from the linked Visit, not a separate ultrasound field."""
        return self.visit.visit_date if self.visit else None

    def __repr__(self):
        return (
            f"<ClinicUltrasoundExam {self.uuid} "
            f"patient={self.patient_id} visit={self.visit_id} type={self.exam_type}>"
        )


class ExternalUltrasoundRequest(db.Model):
    """Lightweight external ultrasound request created from a Visit."""

    __tablename__ = "external_ultrasound_requests"

    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUSES = {
        STATUS_PENDING,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
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

    requested_visit_id = db.Column(
        db.Integer,
        db.ForeignKey("visits.id"),
        nullable=False,
        index=True,
    )

    result_visit_id = db.Column(
        db.Integer,
        db.ForeignKey("visits.id"),
        nullable=True,
        index=True,
    )

    request_note = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(40), nullable=False, default=STATUS_PENDING, index=True)

    result_document_id = db.Column(
        db.Integer,
        db.ForeignKey("patient_documents.id"),
        nullable=True,
        index=True,
    )

    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    completed_by_user_id = db.Column(
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

    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    patient = db.relationship("Patient")
    requested_visit = db.relationship("Visit", foreign_keys=[requested_visit_id])
    result_visit = db.relationship("Visit", foreign_keys=[result_visit_id])
    result_document = db.relationship("PatientDocument", foreign_keys=[result_document_id])
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    completed_by_user = db.relationship("User", foreign_keys=[completed_by_user_id])

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @property
    def is_completed(self):
        return self.status == self.STATUS_COMPLETED

    @property
    def is_cancelled(self):
        return self.status == self.STATUS_CANCELLED

    def __repr__(self):
        return (
            f"<ExternalUltrasoundRequest {self.uuid} "
            f"patient={self.patient_id} status={self.status}>"
        )
