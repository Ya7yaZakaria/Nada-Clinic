import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class InvestigationCategory(db.Model):
    """Dictionary category for investigation tests."""

    __tablename__ = "investigation_categories"

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    code = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name_en = db.Column(db.String(160), nullable=False, index=True)
    name_ar = db.Column(db.String(160), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0, index=True)

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

    def __repr__(self):
        return f"<InvestigationCategory {self.code} {self.name_en}>"


class InvestigationTest(db.Model):
    """Dictionary test that can be ordered or recorded as an external result."""

    __tablename__ = "investigation_tests"

    RESULT_KIND_NUMERIC = "numeric"
    RESULT_KIND_TEXT = "text"
    RESULT_KIND_REPORT = "report"
    RESULT_KIND_COMPOSITE_TEXT = "composite_text"

    RESULT_KINDS = {
        RESULT_KIND_NUMERIC,
        RESULT_KIND_TEXT,
        RESULT_KIND_REPORT,
        RESULT_KIND_COMPOSITE_TEXT,
    }

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("investigation_categories.id"),
        nullable=True,
        index=True,
    )

    code = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name_en = db.Column(db.String(160), nullable=False, index=True)
    name_ar = db.Column(db.String(160), nullable=True, index=True)

    default_unit = db.Column(db.String(80), nullable=True)
    default_reference_range = db.Column(db.String(160), nullable=True)
    result_kind = db.Column(db.String(40), nullable=False, default=RESULT_KIND_TEXT, index=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0, index=True)

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

    category = db.relationship(
        "InvestigationCategory",
        backref=db.backref("tests", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<InvestigationTest {self.code} {self.name_en}>"


class InvestigationOrder(db.Model):
    """Investigation request linked to a patient and usually ordered from a Visit."""

    __tablename__ = "investigation_orders"

    STATUS_DRAFT = "draft"
    STATUS_ORDERED = "ordered"
    STATUS_PARTIALLY_RESULTED = "partially_resulted"
    STATUS_RESULTED = "resulted"
    STATUS_REVIEWED = "reviewed"
    STATUS_CANCELLED = "cancelled"

    STATUSES = {
        STATUS_DRAFT,
        STATUS_ORDERED,
        STATUS_PARTIALLY_RESULTED,
        STATUS_RESULTED,
        STATUS_REVIEWED,
        STATUS_CANCELLED,
    }

    PRIORITY_ROUTINE = "routine"
    PRIORITY_IMPORTANT = "important"
    PRIORITY_URGENT = "urgent"

    PRIORITIES = {
        PRIORITY_ROUTINE,
        PRIORITY_IMPORTANT,
        PRIORITY_URGENT,
    }

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

    ordered_visit_id = db.Column(
        db.Integer,
        db.ForeignKey("visits.id"),
        nullable=True,
        index=True,
    )

    journey_id = db.Column(
        db.Integer,
        db.ForeignKey("journeys.id"),
        nullable=True,
        index=True,
    )

    ordered_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    status = db.Column(db.String(40), nullable=False, default=STATUS_ORDERED, index=True)
    priority = db.Column(db.String(40), nullable=False, default=PRIORITY_ROUTINE, index=True)
    order_notes = db.Column(db.Text, nullable=True)

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
    ordered_visit = db.relationship("Visit", foreign_keys=[ordered_visit_id])
    journey = db.relationship("Journey")
    ordered_by_user = db.relationship("User", foreign_keys=[ordered_by_user_id])

    def __repr__(self):
        return f"<InvestigationOrder {self.uuid} patient={self.patient_id} status={self.status}>"


class InvestigationOrderItem(db.Model):
    """Single requested investigation test inside an order."""

    __tablename__ = "investigation_order_items"

    STATUS_ORDERED = "ordered"
    STATUS_PENDING_RESULT = "pending_result"
    STATUS_RESULT_ENTERED = "result_entered"
    STATUS_REVIEWED = "reviewed"
    STATUS_CANCELLED = "cancelled"

    STATUSES = {
        STATUS_ORDERED,
        STATUS_PENDING_RESULT,
        STATUS_RESULT_ENTERED,
        STATUS_REVIEWED,
        STATUS_CANCELLED,
    }

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("investigation_orders.id"),
        nullable=False,
        index=True,
    )

    test_id = db.Column(
        db.Integer,
        db.ForeignKey("investigation_tests.id"),
        nullable=False,
        index=True,
    )

    status = db.Column(db.String(40), nullable=False, default=STATUS_PENDING_RESULT, index=True)
    item_notes = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0, index=True)

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

    order = db.relationship(
        "InvestigationOrder",
        backref=db.backref(
            "items",
            lazy="dynamic",
            cascade="all, delete-orphan",
        ),
    )
    test = db.relationship("InvestigationTest")

    def __repr__(self):
        return f"<InvestigationOrderItem order={self.order_id} test={self.test_id} status={self.status}>"


class InvestigationResult(db.Model):
    """Result for an ordered investigation item or a historical external investigation."""

    __tablename__ = "investigation_results"

    STATUS_DRAFT = "draft"
    STATUS_ENTERED = "entered"
    STATUS_REVIEWED = "reviewed"
    STATUS_CANCELLED = "cancelled"

    STATUSES = {
        STATUS_DRAFT,
        STATUS_ENTERED,
        STATUS_REVIEWED,
        STATUS_CANCELLED,
    }

    FLAG_UNKNOWN = "unknown"
    FLAG_NORMAL = "normal"
    FLAG_LOW = "low"
    FLAG_HIGH = "high"
    FLAG_ABNORMAL = "abnormal"
    FLAG_CRITICAL = "critical"
    FLAG_NOT_APPLICABLE = "not_applicable"

    ABNORMAL_FLAGS = {
        FLAG_UNKNOWN,
        FLAG_NORMAL,
        FLAG_LOW,
        FLAG_HIGH,
        FLAG_ABNORMAL,
        FLAG_CRITICAL,
        FLAG_NOT_APPLICABLE,
    }

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

    test_id = db.Column(
        db.Integer,
        db.ForeignKey("investigation_tests.id"),
        nullable=False,
        index=True,
    )

    order_item_id = db.Column(
        db.Integer,
        db.ForeignKey("investigation_order_items.id"),
        nullable=True,
        index=True,
    )

    ordered_visit_id = db.Column(
        db.Integer,
        db.ForeignKey("visits.id"),
        nullable=True,
        index=True,
    )

    result_visit_id = db.Column(
        db.Integer,
        db.ForeignKey("visits.id"),
        nullable=True,
        index=True,
    )

    result_date = db.Column(db.Date, nullable=False, index=True)
    lab_name = db.Column(db.String(160), nullable=True, index=True)

    result_value = db.Column(db.String(160), nullable=True)
    unit = db.Column(db.String(80), nullable=True)
    reference_range = db.Column(db.String(160), nullable=True)
    result_text = db.Column(db.Text, nullable=True)
    doctor_comment = db.Column(db.Text, nullable=True)

    abnormal_flag = db.Column(db.String(40), nullable=False, default=FLAG_UNKNOWN, index=True)
    status = db.Column(db.String(40), nullable=False, default=STATUS_ENTERED, index=True)

    has_attachment = db.Column(db.Boolean, nullable=False, default=False, index=True)
    attachment_label = db.Column(db.String(160), nullable=True)
    external_report_reference = db.Column(db.String(255), nullable=True)
    document_id = db.Column(db.Integer, nullable=True, index=True)

    entered_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    reviewed_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    review_note = db.Column(db.Text, nullable=True)

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
    test = db.relationship("InvestigationTest")
    order_item = db.relationship(
        "InvestigationOrderItem",
        backref=db.backref("results", lazy="dynamic"),
    )
    ordered_visit = db.relationship("Visit", foreign_keys=[ordered_visit_id])
    result_visit = db.relationship("Visit", foreign_keys=[result_visit_id])
    entered_by_user = db.relationship("User", foreign_keys=[entered_by_user_id])
    reviewed_by_user = db.relationship("User", foreign_keys=[reviewed_by_user_id])

    def __repr__(self):
        return f"<InvestigationResult patient={self.patient_id} test={self.test_id} date={self.result_date}>"
