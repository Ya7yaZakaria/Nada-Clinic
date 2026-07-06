from flask import Blueprint, render_template
from flask_login import login_required

from app.services.rbac_service import RBACService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/")
@login_required
@RBACService.require_permission("admin.access")
def index():
    return render_template("admin/index.html")
