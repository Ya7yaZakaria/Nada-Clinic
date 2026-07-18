from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.role import user_roles


class User(UserMixin, db.Model):
    """Application user for authentication."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(32), unique=True, nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active_account = db.Column(db.Boolean, nullable=False, default=True)
    is_admin_seed = db.Column(db.Boolean, nullable=False, default=False)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)
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

    roles = db.relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.is_active_account

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def mark_login(self):
        self.last_login_at = datetime.now(timezone.utc)

    def has_role(self, role_name):
        from app.services.rbac_service import (
            RBACService,
        )

        return RBACService.user_has_role(
            self,
            role_name,
        )

    def has_permission(self, permission_name):
        from app.services.rbac_service import (
            RBACService,
        )

        return RBACService.user_has_permission(
            self,
            permission_name,
        )
