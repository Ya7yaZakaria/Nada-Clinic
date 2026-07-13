import uuid as uuid_lib
from datetime import datetime, timezone

from app.extensions import db


class PrintTemplate(db.Model):
    """Reusable visual print layout template for clinic printable documents."""

    __tablename__ = "print_templates"
    __table_args__ = (
        db.UniqueConstraint(
            "document_type",
            "name",
            name="uq_print_templates_document_type_name",
        ),
    )

    DOCUMENT_TYPE_PRESCRIPTION = "prescription"
    DOCUMENT_TYPE_INVESTIGATION_REQUEST = "investigation_request"

    SUPPORTED_DOCUMENT_TYPES = {
        DOCUMENT_TYPE_PRESCRIPTION,
        DOCUMENT_TYPE_INVESTIGATION_REQUEST,
    }

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    name = db.Column(db.String(160), nullable=False, index=True)
    document_type = db.Column(db.String(80), nullable=False, index=True)

    paper_width_mm = db.Column(db.Float, nullable=False, default=148.0)
    paper_height_mm = db.Column(db.Float, nullable=False, default=210.0)

    layout_json = db.Column(db.JSON, nullable=False, default=dict)

    is_default = db.Column(db.Boolean, nullable=False, default=False, index=True)
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

    @staticmethod
    def normalize_name(value):
        return (value or "").strip()

    @classmethod
    def is_supported_document_type(cls, document_type):
        return document_type in cls.SUPPORTED_DOCUMENT_TYPES

    def __repr__(self):
        return f"<PrintTemplate {self.document_type}:{self.name}>"
