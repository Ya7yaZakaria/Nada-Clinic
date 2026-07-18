import uuid
from datetime import UTC, datetime

from app.extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    TYPE_NEW_CONSULTATION = "new_consultation"
    TYPE_FOLLOW_UP = "follow_up"
    TYPE_EMERGENCY = "emergency"

    STATUS_BOOKED = "booked"
    STATUS_ARRIVED = "arrived"
    STATUS_CANCELLED = "cancelled"
    STATUS_RESCHEDULED = "rescheduled"
    STATUS_NO_SHOW = "no_show"

    SOURCE_PHONE = "phone"
    SOURCE_WHATSAPP = "whatsapp"
    SOURCE_CLINIC = "clinic"
    SOURCE_EMERGENCY_UNSCHEDULED = "emergency_unscheduled"

    VALID_TYPES = {
        TYPE_NEW_CONSULTATION,
        TYPE_FOLLOW_UP,
        TYPE_EMERGENCY,
    }

    VALID_STATUSES = {
        STATUS_BOOKED,
        STATUS_ARRIVED,
        STATUS_CANCELLED,
        STATUS_RESCHEDULED,
        STATUS_NO_SHOW,
    }

    VALID_SOURCES = {
        SOURCE_PHONE,
        SOURCE_WHATSAPP,
        SOURCE_CLINIC,
        SOURCE_EMERGENCY_UNSCHEDULED,
    }

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.Time, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)

    appointment_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default=STATUS_BOOKED, index=True)
    source = db.Column(db.String(50), nullable=False, default=SOURCE_CLINIC)

    notes = db.Column(db.Text, nullable=True)
    fee_amount = db.Column(db.Numeric(12, 2), nullable=True)
    paid_amount = db.Column(db.Numeric(12, 2), nullable=True)
    payment_method = db.Column(db.String(40), nullable=True, index=True)
    cancel_reason = db.Column(db.Text, nullable=True)

    arrived_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    no_show_at = db.Column(db.DateTime, nullable=True)
    rescheduled_at = db.Column(db.DateTime, nullable=True)

    rescheduled_from_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)
    rescheduled_to_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    patient = db.relationship("Patient", backref=db.backref("appointments", lazy="dynamic"))
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])
    rescheduled_from = db.relationship("Appointment", remote_side=[id], foreign_keys=[rescheduled_from_id], post_update=True)
    rescheduled_to = db.relationship("Appointment", remote_side=[id], foreign_keys=[rescheduled_to_id], post_update=True)
    visit = db.relationship("Visit", back_populates="appointment", uselist=False)

    def __repr__(self):
        return f"<Appointment {self.uuid} {self.appointment_date} {self.status}>"

