from functools import wraps

from flask import abort
from flask_login import current_user

from app.extensions import db
from app.models import Permission, Role, User


class RBACService:
    """Role-based access control helpers."""

    INITIAL_PERMISSIONS = {
        "dashboard.view": "View dashboard",
        "patients.basic.view": "View basic patient information",
        "patients.basic.create": "Create basic patient records",
        "appointments.view": "View appointments",
        "appointments.manage": "Manage appointments",
        "clinical.view": "View clinical workspace",
        "clinical.note.view": "View clinical notes",
        "clinical.note.write": "Write clinical notes",
        "settings.view": "View settings",
        "settings.manage": "Manage settings",
        "admin.access": "Access admin area",
        "drug_settings.manage": "Manage drug dictionaries and medication settings",
        "prescriptions.view": "View prescriptions",
        "prescriptions.manage": "Manage prescriptions",
    }

    ROLE_PERMISSION_MATRIX = {
        "Admin": list(INITIAL_PERMISSIONS.keys()),
        "Doctor": [
            "dashboard.view",
            "patients.basic.view",
            "appointments.view",
            "clinical.view",
            "clinical.note.view",
            "clinical.note.write",
            "drug_settings.manage",
            "prescriptions.manage",
            "prescriptions.view",
        ],
        "Reception": [
            "dashboard.view",
            "patients.basic.view",
            "patients.basic.create",
            "appointments.view",
            "appointments.manage",
        ],
    }

    @staticmethod
    def user_has_role(user, role_name):
        if not user or not getattr(user, "is_authenticated", False):
            return False

        return any(role.name == role_name for role in user.roles)

    @staticmethod
    def user_has_permission(user, permission_name):
        if not user or not getattr(user, "is_authenticated", False):
            return False

        return any(
            permission.name == permission_name
            for role in user.roles
            for permission in role.permissions
        )

    @staticmethod
    def require_permission(permission_name):
        def decorator(view_func):
            @wraps(view_func)
            def wrapped_view(*args, **kwargs):
                if not RBACService.user_has_permission(current_user, permission_name):
                    abort(403)

                return view_func(*args, **kwargs)

            return wrapped_view

        return decorator

    @staticmethod
    def seed_roles_permissions():
        permissions_by_name = {}

        for permission_name, description in RBACService.INITIAL_PERMISSIONS.items():
            permission = Permission.query.filter_by(name=permission_name).first()

            if not permission:
                group = permission_name.split(".")[0]
                permission = Permission(
                    name=permission_name,
                    description=description,
                    group=group,
                )
                db.session.add(permission)

            permissions_by_name[permission_name] = permission

        db.session.flush()

        for role_name, permission_names in RBACService.ROLE_PERMISSION_MATRIX.items():
            role = Role.query.filter_by(name=role_name).first()

            if not role:
                role = Role(
                    name=role_name,
                    description=f"{role_name} system role",
                    is_system=True,
                )
                db.session.add(role)

            role.permissions = [
                permissions_by_name[permission_name]
                for permission_name in permission_names
            ]

        db.session.commit()

    @staticmethod
    def assign_role(user, role_name):
        role = Role.query.filter_by(name=role_name).first()

        if not role:
            raise ValueError(f"Role does not exist: {role_name}")

        if role not in user.roles:
            user.roles.append(role)
            db.session.commit()

        return user

    @staticmethod
    def assign_roles(user, role_names):
        for role_name in role_names:
            RBACService.assign_role(user, role_name)

        return user

    @staticmethod
    def assign_admin_seed_roles(admin_email):
        user = User.query.filter_by(email=admin_email.strip().lower()).first()

        if not user:
            raise ValueError(f"Admin user does not exist: {admin_email}")

        RBACService.assign_roles(user, ["Admin", "Doctor"])

        return user
