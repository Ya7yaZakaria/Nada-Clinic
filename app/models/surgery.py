import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class SurgeryCase(db.Model):
    """Operational surgery record linked to a patient.

    Surgery starts only when it is scheduled.
    Visit plan text may mention surgery, but no SurgeryCase is created
    until date/time are defined.
    """

    __tablename__ = "surgery_cases"

    STATUS_SCHEDULED = "scheduled"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_POSTPONED = "postponed"

    VALID_STATUSES = {
        STATUS_SCHEDULED,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
        STATUS_POSTPONED,
    }

    CATEGORY_CESAREAN_SECTION = "cesarean_section"
    CATEGORY_HYSTEROSCOPY = "hysteroscopy"
    CATEGORY_LAPAROSCOPY = "laparoscopy"
    CATEGORY_LAPAROTOMY = "laparotomy"
    CATEGORY_D_AND_C = "d_and_c"
    CATEGORY_MINOR_PROCEDURE = "minor_procedure"
    CATEGORY_VAGINAL_SURGERY = "vaginal_surgery"
    CATEGORY_OTHER = "other"

    VALID_CATEGORIES = {
        CATEGORY_CESAREAN_SECTION,
        CATEGORY_HYSTEROSCOPY,
        CATEGORY_LAPAROSCOPY,
        CATEGORY_LAPAROTOMY,
        CATEGORY_D_AND_C,
        CATEGORY_MINOR_PROCEDURE,
        CATEGORY_VAGINAL_SURGERY,
        CATEGORY_OTHER,
    }

    PRIORITY_ROUTINE = "routine"
    PRIORITY_URGENT = "urgent"
    PRIORITY_EMERGENCY = "emergency"

    VALID_PRIORITIES = {
        PRIORITY_ROUTINE,
        PRIORITY_URGENT,
        PRIORITY_EMERGENCY,
    }

    PAYMENT_NOT_RECORDED = "not_recorded"
    PAYMENT_UNPAID = "unpaid"
    PAYMENT_PARTIAL = "partial"
    PAYMENT_PAID = "paid"

    VALID_PAYMENT_STATUSES = {
        PAYMENT_NOT_RECORDED,
        PAYMENT_UNPAID,
        PAYMENT_PARTIAL,
        PAYMENT_PAID,
    }

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    source_visit_id = db.Column(db.Integer, db.ForeignKey("visits.id"), nullable=True, index=True)

    procedure_name = db.Column(db.String(160), nullable=False)
    procedure_category = db.Column(db.String(60), nullable=False, index=True)

    scheduled_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    location = db.Column(db.String(160), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

    status = db.Column(db.String(40), nullable=False, default=STATUS_SCHEDULED, index=True)
    priority = db.Column(db.String(40), nullable=False, default=PRIORITY_ROUTINE, index=True)

    pre_op_note = db.Column(db.Text, nullable=True)
    surgery_note = db.Column(db.Text, nullable=True)

    completed_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    operative_findings = db.Column(db.Text, nullable=True)
    operative_details = db.Column(db.Text, nullable=True)
    complications = db.Column(db.Text, nullable=True)
    post_op_plan = db.Column(db.Text, nullable=True)

    fee_amount = db.Column(db.Numeric(12, 2), nullable=True)
    paid_amount = db.Column(db.Numeric(12, 2), nullable=True)
    payment_status = db.Column(db.String(40), nullable=True, index=True)

    cancel_reason = db.Column(db.Text, nullable=True)
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    cancelled_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

    postponed_reason = db.Column(db.Text, nullable=True)
    postponed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    postponed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    rescheduled_from_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    completed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

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
        backref=db.backref("surgery_cases", lazy="dynamic"),
    )
    source_visit = db.relationship(
        "Visit",
        backref=db.backref("source_surgeries", lazy="dynamic"),
    )
    doctor = db.relationship("User", foreign_keys=[doctor_id])
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    completed_by_user = db.relationship("User", foreign_keys=[completed_by_user_id])
    cancelled_by_user = db.relationship("User", foreign_keys=[cancelled_by_user_id])
    postponed_by_user = db.relationship("User", foreign_keys=[postponed_by_user_id])

    @property
    def is_scheduled(self):
        return self.status == self.STATUS_SCHEDULED

    @property
    def is_completed(self):
        return self.status == self.STATUS_COMPLETED

    @property
    def is_cancelled(self):
        return self.status == self.STATUS_CANCELLED

    @property
    def is_postponed(self):
        return self.status == self.STATUS_POSTPONED

    def __repr__(self):
        return f"<SurgeryCase {self.uuid} patient={self.patient_id} status={self.status}>"
