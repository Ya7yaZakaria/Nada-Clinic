import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class DrugDictionaryMixin:
    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    code = db.Column(db.String(80), nullable=False, unique=True, index=True)
    name_en = db.Column(db.String(120), nullable=False)
    name_ar = db.Column(db.String(120), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

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

    @classmethod
    def normalize_code(cls, value):
        return (value or "").strip().lower().replace(" ", "_")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.code}>"


class DrugCategory(DrugDictionaryMixin, db.Model):
    __tablename__ = "drug_categories"


class DrugForm(DrugDictionaryMixin, db.Model):
    __tablename__ = "drug_forms"


class DrugRoute(DrugDictionaryMixin, db.Model):
    __tablename__ = "drug_routes"


class DrugSafetyStatus(DrugDictionaryMixin, db.Model):
    __tablename__ = "drug_safety_statuses"

    severity_order = db.Column(db.Integer, nullable=False, default=0)
