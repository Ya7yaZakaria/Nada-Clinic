from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.settings_forms import SettingsUpdateForm
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/")
@login_required
@RBACService.require_permission("admin.access")
def index():
    return render_template("admin/index.html")


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("settings.view")
def settings():
    form = SettingsUpdateForm()

    if request.method == "POST":
        if not RBACService.user_has_permission(current_user, "settings.manage"):
            abort(403)

        if form.validate_on_submit():
            grouped_settings = SettingsService.get_grouped_settings()

            for settings_list in grouped_settings.values():
                for setting in settings_list:
                    if not setting.is_editable:
                        continue

                    form_key = f"setting__{setting.key.replace('.', '__')}"
                    posted_value = request.form.get(form_key)

                    if setting.value_type == "boolean":
                        posted_value = "true" if posted_value == "on" else "false"

                    if posted_value is not None:
                        SettingsService.set(setting.key, posted_value)

            flash("Settings updated.", "success")
            return redirect(url_for("admin.settings"))

    grouped_settings = SettingsService.get_grouped_settings()

    return render_template(
        "admin/settings.html",
        form=form,
        grouped_settings=grouped_settings,
    )
