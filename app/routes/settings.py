from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.settings_forms import SettingEditForm, SettingsSeedDefaultsForm
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.get("/")
@login_required
@RBACService.require_permission("settings.view")
def index():
    grouped_settings = SettingsService.grouped_settings_for_ui()
    summary = SettingsService.get_stage_12_summary()
    seed_form = SettingsSeedDefaultsForm()

    return render_template(
        "settings/index.html",
        grouped_settings=grouped_settings,
        summary=summary,
        seed_form=seed_form,
        SettingsService=SettingsService,
    )


@settings_bp.post("/seed-defaults")
@login_required
@RBACService.require_permission("settings.manage")
def seed_defaults():
    form = SettingsSeedDefaultsForm()

    if form.validate_on_submit():
        SettingsService.seed_defaults()
        flash("Default settings seeded and synchronized.", "success")
    else:
        flash("Could not seed settings. Please try again.", "danger")

    return redirect(url_for("settings.index"))


@settings_bp.route("/edit/<path:setting_key>", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("settings.manage")
def edit(setting_key):
    setting = SettingsService.get_setting(setting_key)
    if not setting:
        flash("Setting not found.", "danger")
        return redirect(url_for("settings.index"))

    if not setting.is_editable:
        flash("This setting is not editable.", "warning")
        return redirect(url_for("settings.group", group=setting.group))

    form = SettingEditForm()
    choices = SettingsService.allowed_choices_for_key(setting.key)

    if form.validate_on_submit():
        try:
            if setting.value_type == "boolean":
                value = request.form.get("value", "false")
            elif choices:
                value = request.form.get("value", setting.value)
            else:
                value = request.form.get("value", "")

            SettingsService.update_setting(setting.key, value)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "settings/edit.html",
                form=form,
                setting=setting,
                choices=choices,
                SettingsService=SettingsService,
            )

        flash("Setting updated.", "success")
        return redirect(url_for("settings.group", group=setting.group))

    return render_template(
        "settings/edit.html",
        form=form,
        setting=setting,
        choices=choices,
        SettingsService=SettingsService,
    )


@settings_bp.get("/<group>")
@login_required
@RBACService.require_permission("settings.view")
def group(group):
    settings_list = SettingsService.get_group(group)
    if not settings_list:
        flash("Settings group not found.", "danger")
        return redirect(url_for("settings.index"))

    return render_template(
        "settings/group.html",
        group=group,
        settings_list=settings_list,
        SettingsService=SettingsService,
    )
