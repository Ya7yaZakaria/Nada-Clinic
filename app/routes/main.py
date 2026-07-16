from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

from app.services.dashboard_service import DashboardService
from app.services.rbac_service import RBACService

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
@login_required
@RBACService.require_permission("dashboard.view")
def index():
    can_view_clinical = RBACService.user_has_permission(
        current_user,
        "clinical.view",
    )

    return render_template(
        "index.html",
        today_summary=DashboardService.get_today_summary(),
        recent_patients=DashboardService.get_recent_patients(),
        recent_visits=(
            DashboardService.get_recent_visits()
            if can_view_clinical
            else []
        ),
        can_view_clinical=can_view_clinical,
    )


@main_bp.get("/clinical-placeholder")
@login_required
@RBACService.require_permission("clinical.note.view")
def clinical_placeholder():
    return render_template(
        "placeholders/clinical.html",
        title="Clinical Placeholder",
    )


@main_bp.get("/reception-placeholder")
@login_required
@RBACService.require_permission("appointments.manage")
def reception_placeholder():
    return render_template(
        "placeholders/reception.html",
        title="Reception Placeholder",
    )


@main_bp.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "Nada Clinic System",
            "migration_baseline": "20260715_0069",
        }
    ), 200
