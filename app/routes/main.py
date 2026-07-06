from flask import Blueprint, jsonify, render_template
from flask_login import login_required

from app.services.rbac_service import RBACService

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
@login_required
@RBACService.require_permission("dashboard.view")
def index():
    """Clinic dashboard shell."""

    return render_template("index.html")


@main_bp.get("/clinical-placeholder")
@login_required
@RBACService.require_permission("clinical.note.view")
def clinical_placeholder():
    """Temporary RBAC-only clinical placeholder."""

    return render_template(
        "placeholders/clinical.html",
        title="Clinical Placeholder",
    )


@main_bp.get("/reception-placeholder")
@login_required
@RBACService.require_permission("appointments.manage")
def reception_placeholder():
    """Temporary RBAC-only reception placeholder."""

    return render_template(
        "placeholders/reception.html",
        title="Reception Placeholder",
    )


@main_bp.get("/health")
def health():
    """Health check endpoint."""

    return jsonify(
        {
            "status": "ok",
            "service": "Nada Clinic System",
            "stage": "Stage 1 RBAC Foundation",
        }
    ), 200
