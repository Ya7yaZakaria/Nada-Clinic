import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class PatientDocument(db.Model):
    """Stored patient document metadata. File bytes live in local storage, not in DB."""

    __tablename__ = "patient_documents"

    TYPE_INVESTIGATION_REPORT = "investigation_report"
    TYPE_ULTRASOUND_IMAGE = "ultrasound_image"
    TYPE_ULTRASOUND_REPORT = "ultrasound_report"
    TYPE_OPERATION_REPORT = "operation_report"
    TYPE_CONSENT = "consent"
    TYPE_ID_DOCUMENT = "id_document"
    TYPE_INSURANCE = "insurance"
    TYPE_EXTERNAL_PRESCRIPTION = "external_prescription"
    TYPE_SEMEN_ANALYSIS = "semen_analysis"
    TYPE_PHOTO = "photo"
    TYPE_OTHER = "other"

    DOCUMENT_TYPES = {
        TYPE_INVESTIGATION_REPORT,
        TYPE_ULTRASOUND_IMAGE,
        TYPE_ULTRASOUND_REPORT,
        TYPE_OPERATION_REPORT,
        TYPE_CONSENT,
        TYPE_ID_DOCUMENT,
        TYPE_INSURANCE,
        TYPE_EXTERNAL_PRESCRIPTION,
        TYPE_SEMEN_ANALYSIS,
        TYPE_PHOTO,
        TYPE_OTHER,
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
        nullable=True,
        index=True,
    )

    investigation_result_id = db.Column(
        db.Integer,
        db.ForeignKey("investigation_results.id"),
        nullable=True,
        index=True,
    )

    document_type = db.Column(db.String(80), nullable=False, index=True, default=TYPE_OTHER)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)

    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    storage_path = db.Column(db.String(500), nullable=False)

    mime_type = db.Column(db.String(160), nullable=True)
    file_size = db.Column(db.Integer, nullable=False, default=0)
    checksum = db.Column(db.String(64), nullable=True, index=True)

    uploaded_by_user_id = db.Column(
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

    patient = db.relationship(
        "Patient",
        backref=db.backref("documents", lazy="dynamic"),
    )
    visit = db.relationship(
        "Visit",
        backref=db.backref("documents", lazy="dynamic"),
    )
    investigation_result = db.relationship(
        "InvestigationResult",
        backref=db.backref("documents", lazy="dynamic"),
    )
    uploaded_by_user = db.relationship("User", foreign_keys=[uploaded_by_user_id])

    @property
    def is_image(self):
        return (self.mime_type or "").startswith("image/")

    @property
    def is_pdf(self):
        return self.mime_type == "application/pdf"

    def __repr__(self):
        return f"<PatientDocument {self.uuid} patient={self.patient_id} type={self.document_type}>"
