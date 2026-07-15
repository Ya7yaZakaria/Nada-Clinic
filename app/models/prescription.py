import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class Prescription(db.Model):
    """Structured prescription linked to a patient or partner target.

    Patient prescriptions remain Visit-based.
    Partner prescriptions are linked to patient + partner and may not have a Visit.
    """

    __tablename__ = "prescriptions"

    TARGET_PATIENT = "patient"
    TARGET_PARTNER = "partner"
    VALID_TARGETS = {TARGET_PATIENT, TARGET_PARTNER}

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
        unique=True,
        index=True,
    )

    prescription_target = db.Column(
        db.String(40),
        nullable=False,
        default=TARGET_PATIENT,
        index=True,
    )

    partner_id = db.Column(
        db.Integer,
        db.ForeignKey("partners.id"),
        nullable=True,
        index=True,
    )

    notes = db.Column(db.Text, nullable=True)

    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    updated_by_user_id = db.Column(
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

    patient = db.relationship("Patient")
    visit = db.relationship(
        "Visit",
        backref=db.backref("prescription", uselist=False),
    )
    partner = db.relationship(
        "Partner",
        backref=db.backref("prescriptions", lazy="dynamic"),
    )
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    @property
    def is_partner_target(self):
        return self.prescription_target == self.TARGET_PARTNER

    @property
    def is_patient_target(self):
        return self.prescription_target == self.TARGET_PATIENT

    def __repr__(self):
        return (
            f"<Prescription {self.uuid} target={self.prescription_target} "
            f"visit={self.visit_id} partner={self.partner_id} patient={self.patient_id}>"
        )


class PrescriptionItem(db.Model):
    """Structured medication line inside a prescription."""

    __tablename__ = "prescription_items"

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    prescription_id = db.Column(
        db.Integer,
        db.ForeignKey("prescriptions.id"),
        nullable=False,
        index=True,
    )

    drug_id = db.Column(
        db.Integer,
        db.ForeignKey("drugs.id"),
        nullable=False,
        index=True,
    )

    dose = db.Column(db.String(120), nullable=False)
    frequency = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.String(120), nullable=False)
    instructions_ar = db.Column(db.Text, nullable=False)

    route_id = db.Column(
        db.Integer,
        db.ForeignKey("drug_routes.id"),
        nullable=True,
        index=True,
    )

    sort_order = db.Column(db.Integer, nullable=False, default=0, index=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    prescription = db.relationship(
        "Prescription",
        backref=db.backref(
            "items",
            lazy="dynamic",
            cascade="all, delete-orphan",
        ),
    )
    drug = db.relationship("Drug")
    route = db.relationship("DrugRoute")

    def __repr__(self):
        return f"<PrescriptionItem prescription={self.prescription_id} drug={self.drug_id}>"
