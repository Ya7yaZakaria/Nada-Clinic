from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.drug_forms import DrugForm
from app.models.drug import Drug
from app.models.drug_dictionary import DrugCategory, DrugForm as DrugFormModel, DrugRoute, DrugSafetyStatus
from app.services.drug_dictionary_service import DrugDictionaryService
from app.services.drug_service import DrugService
from app.services.rbac_service import RBACService


drugs_bp = Blueprint("drugs", __name__, url_prefix="/drugs")


def _choice_label(item):
    if item.name_ar:
        return f"{item.name_en} / {item.name_ar}"
    return item.name_en


def _optional_choices(items):
    return [(0, "—")] + [(item.id, _choice_label(item)) for item in items]


def _required_choices(items):
    return [(0, "Select...")] + [(item.id, _choice_label(item)) for item in items]


def _populate_form_choices(form):
    form.category_id.choices = _optional_choices(DrugDictionaryService.get_active_categories())
    form.form_id.choices = _required_choices(DrugDictionaryService.get_active_forms())
    form.route_id.choices = _optional_choices(DrugDictionaryService.get_active_routes())
    safety_choices = _optional_choices(DrugDictionaryService.get_active_safety_statuses())
    form.pregnancy_status_id.choices = safety_choices
    form.lactation_status_id.choices = safety_choices


def _get_or_none(model, item_id):
    if not item_id:
        return None
    return db.session.get(model, item_id)


def _apply_drug_to_form(form, drug):
    form.generic_name.data = drug.generic_name
    form.trade_name.data = drug.trade_name
    form.strength.data = drug.strength
    form.category_id.data = drug.category_id or 0
    form.form_id.data = drug.form_id or 0
    form.route_id.data = drug.route_id or 0
    form.pregnancy_status_id.data = drug.pregnancy_status_id or 0
    form.pregnancy_note.data = drug.pregnancy_note
    form.lactation_status_id.data = drug.lactation_status_id or 0
    form.lactation_note.data = drug.lactation_note
    form.doctor_notes.data = drug.doctor_notes
    form.is_active.data = drug.is_active


def _form_payload(form):
    return {
        "generic_name": form.generic_name.data,
        "trade_name": form.trade_name.data,
        "strength": form.strength.data,
        "category": _get_or_none(DrugCategory, form.category_id.data),
        "form": _get_or_none(DrugFormModel, form.form_id.data),
        "route": _get_or_none(DrugRoute, form.route_id.data),
        "pregnancy_status": _get_or_none(DrugSafetyStatus, form.pregnancy_status_id.data),
        "pregnancy_note": form.pregnancy_note.data,
        "lactation_status": _get_or_none(DrugSafetyStatus, form.lactation_status_id.data),
        "lactation_note": form.lactation_note.data,
        "doctor_notes": form.doctor_notes.data,
    }


@drugs_bp.get("/")
@login_required
@RBACService.require_permission("drug_settings.manage")
def index():
    query = request.args.get("q", "").strip()
    drugs = DrugService.search_drugs(query)

    return render_template("drugs/index.html", drugs=drugs, query=query)


@drugs_bp.route("/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("drug_settings.manage")
def new():
    form = DrugForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        payload = _form_payload(form)

        try:
            DrugService.create_drug(**payload)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("drugs/form.html", form=form, mode="new")

        flash("Drug created.", "success")
        return redirect(url_for("drugs.index"))

    return render_template("drugs/form.html", form=form, mode="new")


@drugs_bp.route("/<drug_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("drug_settings.manage")
def edit(drug_uuid):
    drug = Drug.query.filter_by(uuid=drug_uuid).first_or_404()
    form = DrugForm()
    _populate_form_choices(form)

    if request.method == "GET":
        _apply_drug_to_form(form, drug)

    if form.validate_on_submit():
        payload = _form_payload(form)
        payload["is_active"] = form.is_active.data

        try:
            DrugService.update_drug(drug, **payload)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("drugs/form.html", form=form, mode="edit", drug=drug)

        flash("Drug updated.", "success")
        return redirect(url_for("drugs.index"))

    return render_template("drugs/form.html", form=form, mode="edit", drug=drug)


@drugs_bp.post("/<drug_uuid>/deactivate")
@login_required
@RBACService.require_permission("drug_settings.manage")
def deactivate(drug_uuid):
    drug = Drug.query.filter_by(uuid=drug_uuid).first_or_404()
    DrugService.deactivate_drug(drug)
    flash("Drug deactivated.", "success")
    return redirect(url_for("drugs.index"))


@drugs_bp.post("/<drug_uuid>/reactivate")
@login_required
@RBACService.require_permission("drug_settings.manage")
def reactivate(drug_uuid):
    drug = Drug.query.filter_by(uuid=drug_uuid).first_or_404()
    DrugService.reactivate_drug(drug)
    flash("Drug reactivated.", "success")
    return redirect(url_for("drugs.index"))
