import uuid
from datetime import UTC, datetime

from app.extensions import db


class ClinicDayState(db.Model):
    __tablename__ = "clinic_day_states"

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )

    clinic_date = db.Column(
        db.Date,
        unique=True,
        nullable=False,
        index=True,
    )

    is_closed = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    closed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    reopened_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    def __repr__(self):
        return (
            f"<ClinicDayState {self.clinic_date} "
            f"closed={self.is_closed}>"
        )