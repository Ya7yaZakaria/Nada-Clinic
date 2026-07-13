import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class InvestigationPreset(db.Model):
    """Reusable global investigation panel/workup managed by doctors/admins."""

    __tablename__ = "investigation_presets"

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
        "InvestigationPresetItem",
        back_populates="preset",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @staticmethod
    def normalize_name(value):
        return (value or "").strip()

    def __repr__(self):
        return f"<InvestigationPreset {self.name}>"


class InvestigationPresetItem(db.Model):
    """Single investigation test inside a reusable investigation preset/panel."""

    __tablename__ = "investigation_preset_items"

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
        db.ForeignKey("investigation_presets.id"),
        nullable=False,
        index=True,
    )

    test_id = db.Column(
        db.Integer,
        db.ForeignKey("investigation_tests.id"),
        nullable=False,
        index=True,
    )

    sort_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    preset = db.relationship("InvestigationPreset", back_populates="items")
    test = db.relationship("InvestigationTest")

    def __repr__(self):
        return f"<InvestigationPresetItem preset={self.preset_id} test={self.test_id}>"
