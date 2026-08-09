from flask import (
    current_app,
    g,
    has_request_context,
    session,
)

from app.models.role import Role


class DevelopmentRolePreviewService:
    """Development-only session role preview helpers."""

    SESSION_KEY = "development_role_preview"
    REQUEST_ROLE_CACHE_KEY = "_development_role_preview_role"

    @staticmethod
    def _allowed_emails():
        configured = current_app.config.get(
            "DEV_ROLE_PREVIEW_EMAILS",
            "",
        )

        if isinstance(configured, str):
            values = configured.split(",")
        else:
            values = configured or []

        return {
            str(value).strip().lower()
            for value in values
            if str(value).strip()
        }

    @staticmethod
    def is_enabled():
        return bool(
            current_app.config.get(
                "DEV_ROLE_PREVIEW_ENABLED",
                False,
            )
        )

    @staticmethod
    def can_preview(user):
        if not DevelopmentRolePreviewService.is_enabled():
            return False

        if not user or not getattr(
            user,
            "is_authenticated",
            False,
        ):
            return False

        email = str(
            getattr(user, "email", "") or ""
        ).strip().lower()

        return email in (
            DevelopmentRolePreviewService
            ._allowed_emails()
        )

    @staticmethod
    def available_role_names():
        roles = Role.query.order_by(Role.name.asc()).all()
        return tuple(role.name for role in roles)

    @staticmethod
    def _find_role(role_name):
        if not role_name:
            return None

        if has_request_context():
            cached_role = getattr(
                g,
                DevelopmentRolePreviewService.REQUEST_ROLE_CACHE_KEY,
                None,
            )
            if cached_role is not None and cached_role.name == role_name:
                return cached_role

        role = Role.query.filter_by(name=role_name).first()

        if role is not None and has_request_context():
            setattr(
                g,
                DevelopmentRolePreviewService.REQUEST_ROLE_CACHE_KEY,
                role,
            )

        return role

    @staticmethod
    def _preview_role_record(user):
        if not has_request_context():
            return None

        if not DevelopmentRolePreviewService.can_preview(user):
            DevelopmentRolePreviewService.clear_preview_role()
            return None

        role = DevelopmentRolePreviewService._find_role(
            session.get(DevelopmentRolePreviewService.SESSION_KEY)
        )

        if role is None:
            DevelopmentRolePreviewService.clear_preview_role()

        return role

    @staticmethod
    def get_preview_role(user):
        role = DevelopmentRolePreviewService._preview_role_record(user)
        return role.name if role is not None else None

    @staticmethod
    def preview_permission_names(user):
        role = DevelopmentRolePreviewService._preview_role_record(user)

        if role is None:
            return None

        return {permission.name for permission in role.permissions}

    @staticmethod
    def set_preview_role(user, role_name):
        if not DevelopmentRolePreviewService.can_preview(user):
            raise PermissionError(
                "Development role preview is unavailable."
            )

        role = DevelopmentRolePreviewService._find_role(role_name)

        if role is None:
            raise ValueError(
                "Unsupported development preview role."
            )

        session[DevelopmentRolePreviewService.SESSION_KEY] = role.name
        return role.name

    @staticmethod
    def clear_preview_role():
        if not has_request_context():
            return

        session.pop(DevelopmentRolePreviewService.SESSION_KEY, None)

        if hasattr(
            g,
            DevelopmentRolePreviewService.REQUEST_ROLE_CACHE_KEY,
        ):
            delattr(
                g,
                DevelopmentRolePreviewService.REQUEST_ROLE_CACHE_KEY,
            )

    @staticmethod
    def actual_role_names(user):
        if not user or not getattr(
            user,
            "is_authenticated",
            False,
        ):
            return []

        return sorted(
            role.name
            for role in getattr(user, "roles", [])
        )

    @staticmethod
    def effective_role_names(user):
        preview_role = DevelopmentRolePreviewService.get_preview_role(user)

        if preview_role:
            return [preview_role]

        return DevelopmentRolePreviewService.actual_role_names(user)

    @staticmethod
    def template_context(user):
        enabled = DevelopmentRolePreviewService.can_preview(user)
        preview_role = (
            DevelopmentRolePreviewService.get_preview_role(user)
            if enabled
            else None
        )

        return {
            "enabled": enabled,
            "active": preview_role is not None,
            "preview_role": preview_role,
            "available_roles": (
                DevelopmentRolePreviewService.available_role_names()
                if enabled
                else ()
            ),
            "actual_roles": (
                DevelopmentRolePreviewService.actual_role_names(user)
            ),
            "effective_roles": (
                DevelopmentRolePreviewService.effective_role_names(user)
            ),
        }
