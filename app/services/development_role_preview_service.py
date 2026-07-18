
from flask import (
    current_app,
    has_request_context,
    session,
)


class DevelopmentRolePreviewService:
    """Development-only session role preview helpers."""

    SESSION_KEY = "development_role_preview"
    AVAILABLE_ROLES = (
        "Admin",
        "Doctor",
        "Reception",
    )

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
    def get_preview_role(user):
        if not has_request_context():
            return None

        if not DevelopmentRolePreviewService.can_preview(
            user
        ):
            session.pop(
                DevelopmentRolePreviewService.SESSION_KEY,
                None,
            )
            return None

        role_name = session.get(
            DevelopmentRolePreviewService.SESSION_KEY
        )

        if role_name not in (
            DevelopmentRolePreviewService
            .AVAILABLE_ROLES
        ):
            session.pop(
                DevelopmentRolePreviewService.SESSION_KEY,
                None,
            )
            return None

        return role_name

    @staticmethod
    def set_preview_role(user, role_name):
        if not DevelopmentRolePreviewService.can_preview(
            user
        ):
            raise PermissionError(
                "Development role preview is unavailable."
            )

        if role_name not in (
            DevelopmentRolePreviewService
            .AVAILABLE_ROLES
        ):
            raise ValueError(
                "Unsupported development preview role."
            )

        session[
            DevelopmentRolePreviewService.SESSION_KEY
        ] = role_name

        return role_name

    @staticmethod
    def clear_preview_role():
        if not has_request_context():
            return

        session.pop(
            DevelopmentRolePreviewService.SESSION_KEY,
            None,
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
        preview_role = (
            DevelopmentRolePreviewService
            .get_preview_role(user)
        )

        if preview_role:
            return [preview_role]

        return (
            DevelopmentRolePreviewService
            .actual_role_names(user)
        )

    @staticmethod
    def template_context(user):
        enabled = (
            DevelopmentRolePreviewService
            .can_preview(user)
        )
        preview_role = (
            DevelopmentRolePreviewService
            .get_preview_role(user)
            if enabled
            else None
        )

        return {
            "enabled": enabled,
            "active": preview_role is not None,
            "preview_role": preview_role,
            "available_roles": (
                DevelopmentRolePreviewService
                .AVAILABLE_ROLES
            ),
            "actual_roles": (
                DevelopmentRolePreviewService
                .actual_role_names(user)
            ),
            "effective_roles": (
                DevelopmentRolePreviewService
                .effective_role_names(user)
            ),
        }
