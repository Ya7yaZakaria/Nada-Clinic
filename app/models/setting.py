from datetime import datetime, timezone

from app.extensions import db


class Setting(db.Model):
    """Configurable clinic/system setting."""

    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    value_type = db.Column(db.String(30), nullable=False, default="string")
    group = db.Column(db.String(80), nullable=False, index=True)
    label = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    is_editable = db.Column(db.Boolean, nullable=False, default=True)
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

    def cast_value(self):
        if self.value_type == "boolean":
            return str(self.value).lower() in ("1", "true", "yes", "on")

        if self.value_type == "integer":
            try:
                return int(self.value)
            except (TypeError, ValueError):
                return 0

        return self.value

    def __repr__(self):
        return f"<Setting {self.key}>"
