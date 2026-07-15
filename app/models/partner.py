import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class Partner(db.Model):
    """Patient-linked partner/husband record.

    Partner is not a full Patient record. It is a clinical companion record
    used mainly for infertility workflows.
    """

    __tablename__ = "partners"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)

    name = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(40), nullable=True)
    age_years = db.Column(db.Integer, nullable=True)
    occupation = db.Column(db.String(160), nullable=True)

    previous_children = db.Column(db.Text, nullable=True)
    fertility_notes = db.Column(db.Text, nullable=True)
    medical_notes = db.Column(db.Text, nullable=True)

    follow_up_note = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.Date, nullable=True, index=True)

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
        backref=db.backref("partners", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<Partner {self.uuid} patient={self.patient_id} active={self.is_active}>"


class PartnerSemenAnalysis(db.Model):
    """Simple partner semen analysis record.

    Stage 10 stores SA as date + notes + optional uploaded document only.
    Structured semen parameters are intentionally deferred.
    """

    __tablename__ = "partner_semen_analyses"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey("patient_documents.id"), nullable=True, index=True)

    analysis_date = db.Column(db.Date, nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

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

    partner = db.relationship(
        "Partner",
        backref=db.backref("semen_analyses", lazy="dynamic"),
    )
    patient = db.relationship("Patient")
    document = db.relationship("PatientDocument")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])

    def __repr__(self):
        return f"<PartnerSemenAnalysis {self.uuid} partner={self.partner_id} date={self.analysis_date}>"
