import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class Drug(db.Model):
    """Clinic medication database item."""

    __tablename__ = "drugs"

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    generic_name = db.Column(db.String(160), nullable=False, index=True)
    trade_name = db.Column(db.String(160), nullable=False, index=True)
    strength = db.Column(db.String(80), nullable=False, index=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("drug_categories.id"),
        nullable=True,
        index=True,
    )
    form_id = db.Column(
        db.Integer,
        db.ForeignKey("drug_forms.id"),
        nullable=False,
        index=True,
    )
    route_id = db.Column(
        db.Integer,
        db.ForeignKey("drug_routes.id"),
        nullable=True,
        index=True,
    )

    pregnancy_status_id = db.Column(
        db.Integer,
        db.ForeignKey("drug_safety_statuses.id"),
        nullable=True,
        index=True,
    )
    pregnancy_note = db.Column(db.Text, nullable=True)

    lactation_status_id = db.Column(
        db.Integer,
        db.ForeignKey("drug_safety_statuses.id"),
        nullable=True,
        index=True,
    )
    lactation_note = db.Column(db.Text, nullable=True)

    doctor_notes = db.Column(db.Text, nullable=True)

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

    category = db.relationship("DrugCategory", foreign_keys=[category_id])
    form = db.relationship("DrugForm", foreign_keys=[form_id])
    route = db.relationship("DrugRoute", foreign_keys=[route_id])
    pregnancy_status = db.relationship("DrugSafetyStatus", foreign_keys=[pregnancy_status_id])
    lactation_status = db.relationship("DrugSafetyStatus", foreign_keys=[lactation_status_id])

    __table_args__ = (
        db.UniqueConstraint(
            "trade_name",
            "form_id",
            "strength",
            name="uq_drugs_trade_form_strength",
        ),
    )

    @staticmethod
    def normalize_name(value):
        return (value or "").strip()

    @staticmethod
    def normalize_strength(value):
        return (value or "").strip()

    def __repr__(self):
        return f"<Drug {self.trade_name} {self.strength}>"
