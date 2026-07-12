from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.forms.prescription_preset_forms import PrescriptionPresetForm, PrescriptionPresetItemForm
from app.models.drug import Drug
from app.models.drug_dictionary import DrugRoute
from app.models.prescription_preset import PrescriptionPreset, PrescriptionPresetItem
from app.services.drug_dictionary_service import DrugDictionaryService
from app.services.drug_service import DrugService
from app.services.prescription_preset_service import PrescriptionPresetService
from app.services.rbac_service import RBACService

prescription_presets_bp = Blueprint(
    "prescription_presets",
    __name__,
    url_prefix="/prescription-presets",
)


def _choice_label(item):
    if getattr(item, "name_ar", None):
        return f"{item.name_en} / {item.name_ar}"
    return item.name_en


def _drug_choice_label(drug):
    form_name = drug.form.name_en if drug.form else "-"
    return f"{drug.trade_name} {drug.strength} - {drug.generic_name} ({form_name})"


def _populate_item_form_choices(form):
    form.drug_id.choices = [(0, "Select drug...")] + [
        (drug.id, _drug_choice_label(drug))
        for drug in DrugService.get_active_drugs()
    ]
    form.route_id.choices = [(0, "Use drug default route")] + [
        (route.id, _choice_label(route))
        for route in DrugDictionaryService.get_active_routes()
    ]


def _get_drug_or_none(drug_id):
    if not drug_id:
        return None
    return Drug.query.filter_by(id=drug_id, is_active=True).first()


def _get_route_or_none(route_id):
    if not route_id:
        return None
    return DrugRoute.query.filter_by(id=route_id, is_active=True).first()


def _apply_preset_to_form(form, preset):
    form.name.data = preset.name
    form.description.data = preset.description
    form.is_active.data = preset.is_active


def _apply_item_to_form(form, item):
    form.drug_id.data = item.drug_id
    form.route_id.data = item.route_id or 0
    form.dose.data = item.dose
    form.frequency.data = item.frequency
    form.duration.data = item.duration
    form.instructions_ar.data = item.instructions_ar


@prescription_presets_bp.get("/")
@login_required
@RBACService.require_permission("prescription_presets.manage")
def index():
    presets = PrescriptionPresetService.list_all_presets()
    return render_template("prescription_presets/index.html", presets=presets)


@prescription_presets_bp.route("/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("prescription_presets.manage")
def new():
    form = PrescriptionPresetForm()

    if form.validate_on_submit():
        try:
            preset = PrescriptionPresetService.create_preset(
                name=form.name.data,
                description=form.description.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("prescription_presets/form.html", form=form, mode="new")

        flash("Prescription preset created.", "success")
        return redirect(url_for("prescription_presets.detail", preset_uuid=preset.uuid))

    return render_template("prescription_presets/form.html", form=form, mode="new")


@prescription_presets_bp.get("/<preset_uuid>")
@login_required
@RBACService.require_permission("prescription_presets.manage")
def detail(preset_uuid):
    preset = PrescriptionPreset.query.filter_by(uuid=preset_uuid).first_or_404()
    items = PrescriptionPresetService.list_items(preset)

    item_form = PrescriptionPresetItemForm()
    _populate_item_form_choices(item_form)

    return render_template(
        "prescription_presets/detail.html",
        preset=preset,
        items=items,
        item_form=item_form,
    )


@prescription_presets_bp.route("/<preset_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("prescription_presets.manage")
def edit(preset_uuid):
    preset = PrescriptionPreset.query.filter_by(uuid=preset_uuid).first_or_404()
    form = PrescriptionPresetForm()

    if form.validate_on_submit():
        try:
            PrescriptionPresetService.update_preset(
                preset,
                name=form.name.data,
                description=form.description.data,
                is_active=form.is_active.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "prescription_presets/form.html",
                form=form,
                mode="edit",
                preset=preset,
            )

        flash("Prescription preset updated.", "success")
        return redirect(url_for("prescription_presets.detail", preset_uuid=preset.uuid))

    if form.is_submitted() is False:
        _apply_preset_to_form(form, preset)

    return render_template(
        "prescription_presets/form.html",
        form=form,
        mode="edit",
        preset=preset,
    )


@prescription_presets_bp.post("/<preset_uuid>/deactivate")
@login_required
@RBACService.require_permission("prescription_presets.manage")
def deactivate(preset_uuid):
    preset = PrescriptionPreset.query.filter_by(uuid=preset_uuid).first_or_404()
    PrescriptionPresetService.update_preset(
        preset,
        is_active=False,
        actor_user=current_user,
    )
    flash("Prescription preset deactivated.", "success")
    return redirect(url_for("prescription_presets.index"))


@prescription_presets_bp.post("/<preset_uuid>/reactivate")
@login_required
@RBACService.require_permission("prescription_presets.manage")
def reactivate(preset_uuid):
    preset = PrescriptionPreset.query.filter_by(uuid=preset_uuid).first_or_404()
    PrescriptionPresetService.update_preset(
        preset,
        is_active=True,
        actor_user=current_user,
    )
    flash("Prescription preset reactivated.", "success")
    return redirect(url_for("prescription_presets.index"))


@prescription_presets_bp.post("/<preset_uuid>/items")
@login_required
@RBACService.require_permission("prescription_presets.manage")
def add_item(preset_uuid):
    preset = PrescriptionPreset.query.filter_by(uuid=preset_uuid).first_or_404()

    form = PrescriptionPresetItemForm()
    _populate_item_form_choices(form)

    if not form.validate_on_submit():
        flash("Invalid preset item.", "danger")
        return redirect(url_for("prescription_presets.detail", preset_uuid=preset.uuid))

    drug = _get_drug_or_none(form.drug_id.data)
    route = _get_route_or_none(form.route_id.data)

    try:
        PrescriptionPresetService.add_item(
            preset=preset,
            drug=drug,
            dose=form.dose.data,
            frequency=form.frequency.data,
            duration=form.duration.data,
            instructions_ar=form.instructions_ar.data,
            route=route,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("prescription_presets.detail", preset_uuid=preset.uuid))

    flash("Preset medication added.", "success")
    return redirect(url_for("prescription_presets.detail", preset_uuid=preset.uuid))


@prescription_presets_bp.route("/items/<item_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("prescription_presets.manage")
def edit_item(item_uuid):
    item = PrescriptionPresetItem.query.filter_by(uuid=item_uuid).first_or_404()
    preset = item.preset

    form = PrescriptionPresetItemForm()
    _populate_item_form_choices(form)

    if form.validate_on_submit():
        drug = _get_drug_or_none(form.drug_id.data)
        route = _get_route_or_none(form.route_id.data)

        try:
            PrescriptionPresetService.update_item(
                item,
                drug=drug,
                dose=form.dose.data,
                frequency=form.frequency.data,
                duration=form.duration.data,
                instructions_ar=form.instructions_ar.data,
                route=route,
            )
            PrescriptionPresetService.update_preset(
                preset,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "prescription_presets/item_form.html",
                form=form,
                item=item,
                preset=preset,
            )

        flash("Preset medication updated.", "success")
        return redirect(url_for("prescription_presets.detail", preset_uuid=preset.uuid))

    if form.is_submitted() is False:
        _apply_item_to_form(form, item)

    return render_template(
        "prescription_presets/item_form.html",
        form=form,
        item=item,
        preset=preset,
    )


@prescription_presets_bp.post("/items/<item_uuid>/remove")
@login_required
@RBACService.require_permission("prescription_presets.manage")
def remove_item(item_uuid):
    item = PrescriptionPresetItem.query.filter_by(uuid=item_uuid).first_or_404()
    preset = item.preset

    PrescriptionPresetService.remove_item(item)
    PrescriptionPresetService.update_preset(
        preset,
        actor_user=current_user,
    )

    flash("Preset medication removed.", "success")
    return redirect(url_for("prescription_presets.detail", preset_uuid=preset.uuid))
