import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class PrescriptionPreset(db.Model):
    """Reusable global prescription preset managed by doctors/admins."""

    __tablename__ = "prescription_presets"

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    name = db.Column(db.String(160), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)

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

    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    items = db.relationship(
        "PrescriptionPresetItem",
        back_populates="preset",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @staticmethod
    def normalize_name(value):
        return (value or "").strip()

    def __repr__(self):
        return f"<PrescriptionPreset {self.name}>"


class PrescriptionPresetItem(db.Model):
    """Structured medication line inside a reusable prescription preset."""

    __tablename__ = "prescription_preset_items"

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    preset_id = db.Column(
        db.Integer,
        db.ForeignKey("prescription_presets.id"),
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

    preset = db.relationship("PrescriptionPreset", back_populates="items")
    drug = db.relationship("Drug")
    route = db.relationship("DrugRoute")

    def __repr__(self):
        return f"<PrescriptionPresetItem preset={self.preset_id} drug={self.drug_id}>"
