
from flask import (
    Blueprint,
    abort,
    redirect,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.services.development_role_preview_service import (
    DevelopmentRolePreviewService,
)


development_bp = Blueprint(
    "development",
    __name__,
    url_prefix="/development",
)


@development_bp.post("/role-preview")
@login_required
def set_role_preview():
    if not DevelopmentRolePreviewService.can_preview(
        current_user
    ):
        abort(404)

    role_name = str(
        request.form.get("role_name", "")
    ).strip()

    try:
        DevelopmentRolePreviewService.set_preview_role(
            current_user,
            role_name,
        )
    except ValueError:
        abort(400)

    return redirect(url_for("main.index"))


@development_bp.post("/role-preview/clear")
@login_required
def clear_role_preview():
    if not DevelopmentRolePreviewService.can_preview(
        current_user
    ):
        abort(404)

    DevelopmentRolePreviewService.clear_preview_role()

    return redirect(url_for("main.index"))
