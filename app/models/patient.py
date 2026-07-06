import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class Patient(db.Model):
    """Root patient entity for the clinic system."""

    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    medical_file_number = db.Column(
        db.Integer,
        unique=True,
        nullable=False,
        index=True,
    )

    name_ar = db.Column(db.String(160), nullable=False, index=True)
    name_en = db.Column(db.String(160), nullable=False, index=True)
    search_name = db.Column(db.String(360), nullable=False, index=True)

    gender = db.Column(db.String(20), nullable=False, default="female")

    date_of_birth = db.Column(db.Date, nullable=True)
    age_years_at_registration = db.Column(db.Integer, nullable=True)
    age_recorded_at = db.Column(db.Date, nullable=True)

    marital_status = db.Column(db.String(30), nullable=False, default="unknown")
    is_virgin = db.Column(db.Boolean, nullable=False, default=False)

    occupation = db.Column(db.String(120), nullable=True)

    phone_primary = db.Column(db.String(40), nullable=False, index=True)
    phone_secondary = db.Column(db.String(40), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=True)

    governorate = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    street = db.Column(db.String(255), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)

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

    @property
    def formatted_mrn(self):
        return f"{self.medical_file_number:06d}"

    def __repr__(self):
        return f"<Patient {self.formatted_mrn} {self.name_en}>"
