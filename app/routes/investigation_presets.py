from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.forms.investigation_preset_forms import InvestigationPresetForm, InvestigationPresetItemForm
from app.models.investigation import InvestigationTest
from app.models.investigation_preset import InvestigationPreset, InvestigationPresetItem
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_preset_service import InvestigationPresetService
from app.services.rbac_service import RBACService


investigation_presets_bp = Blueprint(
    "investigation_presets",
    __name__,
    url_prefix="/investigation-presets",
)


def _test_choice_label(test):
    category_name = test.category.name_en if test.category else "Uncategorized"
    if test.default_unit:
        return f"{test.name_en} ({category_name}) — {test.default_unit}"
    return f"{test.name_en} ({category_name})"


def _populate_item_form_choices(form):
    form.test_id.choices = [(0, "Select investigation test...")] + [
        (test.id, _test_choice_label(test))
        for test in InvestigationDictionaryService.list_active_tests()
    ]


def _get_active_test_or_none(test_id):
    if not test_id:
        return None
    return InvestigationTest.query.filter_by(id=test_id, is_active=True).first()


def _apply_preset_to_form(form, preset):
    form.name.data = preset.name
    form.description.data = preset.description
    form.is_active.data = preset.is_active


@investigation_presets_bp.get("/")
@login_required
@RBACService.require_permission("investigation_presets.manage")
def index():
    presets = InvestigationPresetService.list_all_presets()
    return render_template("investigation_presets/index.html", presets=presets)


@investigation_presets_bp.route("/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("investigation_presets.manage")
def new():
    form = InvestigationPresetForm()

    if form.validate_on_submit():
        try:
            preset = InvestigationPresetService.create_preset(
                name=form.name.data,
                description=form.description.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("investigation_presets/form.html", form=form, mode="new")

        flash("Investigation preset created.", "success")
        return redirect(url_for("investigation_presets.detail", preset_uuid=preset.uuid))

    return render_template("investigation_presets/form.html", form=form, mode="new")


@investigation_presets_bp.get("/<preset_uuid>")
@login_required
@RBACService.require_permission("investigation_presets.manage")
def detail(preset_uuid):
    preset = InvestigationPreset.query.filter_by(uuid=preset_uuid).first_or_404()
    items = InvestigationPresetService.list_items(preset)

    item_form = InvestigationPresetItemForm()
    _populate_item_form_choices(item_form)

    return render_template(
        "investigation_presets/detail.html",
        preset=preset,
        items=items,
        item_form=item_form,
    )


@investigation_presets_bp.route("/<preset_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("investigation_presets.manage")
def edit(preset_uuid):
    preset = InvestigationPreset.query.filter_by(uuid=preset_uuid).first_or_404()
    form = InvestigationPresetForm()

    if form.validate_on_submit():
        try:
            InvestigationPresetService.update_preset(
                preset,
                name=form.name.data,
                description=form.description.data,
                is_active=form.is_active.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "investigation_presets/form.html",
                form=form,
                mode="edit",
                preset=preset,
            )

        flash("Investigation preset updated.", "success")
        return redirect(url_for("investigation_presets.detail", preset_uuid=preset.uuid))

    if form.is_submitted() is False:
        _apply_preset_to_form(form, preset)

    return render_template(
        "investigation_presets/form.html",
        form=form,
        mode="edit",
        preset=preset,
    )


@investigation_presets_bp.post("/<preset_uuid>/deactivate")
@login_required
@RBACService.require_permission("investigation_presets.manage")
def deactivate(preset_uuid):
    preset = InvestigationPreset.query.filter_by(uuid=preset_uuid).first_or_404()
    InvestigationPresetService.deactivate_preset(
        preset,
        actor_user=current_user,
    )
    flash("Investigation preset deactivated.", "success")
    return redirect(url_for("investigation_presets.index"))


@investigation_presets_bp.post("/<preset_uuid>/reactivate")
@login_required
@RBACService.require_permission("investigation_presets.manage")
def reactivate(preset_uuid):
    preset = InvestigationPreset.query.filter_by(uuid=preset_uuid).first_or_404()
    InvestigationPresetService.reactivate_preset(
        preset,
        actor_user=current_user,
    )
    flash("Investigation preset reactivated.", "success")
    return redirect(url_for("investigation_presets.index"))


@investigation_presets_bp.post("/<preset_uuid>/items")
@login_required
@RBACService.require_permission("investigation_presets.manage")
def add_item(preset_uuid):
    preset = InvestigationPreset.query.filter_by(uuid=preset_uuid).first_or_404()

    form = InvestigationPresetItemForm()
    _populate_item_form_choices(form)

    if not form.validate_on_submit():
        flash("Invalid investigation preset item.", "danger")
        return redirect(url_for("investigation_presets.detail", preset_uuid=preset.uuid))

    test = _get_active_test_or_none(form.test_id.data)

    try:
        InvestigationPresetService.add_item(
            preset=preset,
            test=test,
            notes=form.notes.data,
        )
        InvestigationPresetService.update_preset(
            preset,
            actor_user=current_user,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("investigation_presets.detail", preset_uuid=preset.uuid))

    flash("Investigation test added to preset.", "success")
    return redirect(url_for("investigation_presets.detail", preset_uuid=preset.uuid))


@investigation_presets_bp.post("/items/<item_uuid>/remove")
@login_required
@RBACService.require_permission("investigation_presets.manage")
def remove_item(item_uuid):
    item = InvestigationPresetItem.query.filter_by(uuid=item_uuid).first_or_404()
    preset = item.preset

    InvestigationPresetService.remove_item(item)
    InvestigationPresetService.update_preset(
        preset,
        actor_user=current_user,
    )

    flash("Investigation preset item removed.", "success")
    return redirect(url_for("investigation_presets.detail", preset_uuid=preset.uuid))
