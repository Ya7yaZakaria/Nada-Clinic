from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import login_required

from app.forms.drug_dictionary_forms import DrugDictionaryForm, DrugSafetyStatusForm
from app.models.drug_dictionary import DrugCategory, DrugForm, DrugRoute, DrugSafetyStatus
from app.services.drug_dictionary_service import DrugDictionaryService
from app.services.rbac_service import RBACService


drug_settings_bp = Blueprint("drug_settings", __name__, url_prefix="/drug-settings")


DICTIONARY_CONFIG = {
    "categories": {
        "model": DrugCategory,
        "label": "Drug Categories",
        "singular": "Drug Category",
        "form": DrugDictionaryForm,
        "create": DrugDictionaryService.create_category,
        "update": DrugDictionaryService.update_category,
    },
    "forms": {
        "model": DrugForm,
        "label": "Drug Forms",
        "singular": "Drug Form",
        "form": DrugDictionaryForm,
        "create": DrugDictionaryService.create_form,
        "update": DrugDictionaryService.update_form,
    },
    "routes": {
        "model": DrugRoute,
        "label": "Drug Routes",
        "singular": "Drug Route",
        "form": DrugDictionaryForm,
        "create": DrugDictionaryService.create_route,
        "update": DrugDictionaryService.update_route,
    },
    "safety-statuses": {
        "model": DrugSafetyStatus,
        "label": "Drug Safety Statuses",
        "singular": "Drug Safety Status",
        "form": DrugSafetyStatusForm,
        "create": DrugDictionaryService.create_safety_status,
        "update": DrugDictionaryService.update_safety_status,
    },
}


def _get_config(dictionary_type):
    config = DICTIONARY_CONFIG.get(dictionary_type)
    if not config:
        abort(404)
    return config


def _get_item_or_404(config, item_uuid):
    return config["model"].query.filter_by(uuid=item_uuid).first_or_404()


@drug_settings_bp.get("/")
@login_required
@RBACService.require_permission("drug_settings.manage")
def index():
    dictionaries = {
        key: {
            "label": config["label"],
            "singular": config["singular"],
            "records": config["model"].query.order_by(
                config["model"].sort_order.asc(),
                config["model"].name_en.asc(),
            ).all(),
        }
        for key, config in DICTIONARY_CONFIG.items()
    }

    return render_template("drug_settings/index.html", dictionaries=dictionaries)


@drug_settings_bp.post("/seed-defaults")
@login_required
@RBACService.require_permission("drug_settings.manage")
def seed_defaults():
    DrugDictionaryService.seed_defaults()
    flash("Default medication dictionaries seeded.", "success")
    return redirect(url_for("drug_settings.index"))


@drug_settings_bp.route("/<dictionary_type>/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("drug_settings.manage")
def new(dictionary_type):
    config = _get_config(dictionary_type)
    form = config["form"]()

    if form.validate_on_submit():
        try:
            kwargs = {
                "code": form.code.data,
                "name_en": form.name_en.data,
                "name_ar": form.name_ar.data,
                "sort_order": form.sort_order.data or 0,
            }

            if dictionary_type == "safety-statuses":
                kwargs["severity_order"] = form.severity_order.data or 0

            config["create"](**kwargs)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "drug_settings/form.html",
                form=form,
                dictionary_type=dictionary_type,
                config=config,
                mode="new",
            )

        flash(f"{config['singular']} created.", "success")
        return redirect(url_for("drug_settings.index"))

    return render_template(
        "drug_settings/form.html",
        form=form,
        dictionary_type=dictionary_type,
        config=config,
        mode="new",
    )


@drug_settings_bp.route("/<dictionary_type>/<item_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("drug_settings.manage")
def edit(dictionary_type, item_uuid):
    config = _get_config(dictionary_type)
    item = _get_item_or_404(config, item_uuid)

    form = config["form"](obj=item)

    if dictionary_type == "safety-statuses" and hasattr(form, "severity_order") and not form.is_submitted():
        form.severity_order.data = item.severity_order

    if form.validate_on_submit():
        try:
            kwargs = {
                "code": form.code.data,
                "name_en": form.name_en.data,
                "name_ar": form.name_ar.data,
                "sort_order": form.sort_order.data or 0,
                "is_active": form.is_active.data,
            }

            if dictionary_type == "safety-statuses":
                kwargs["severity_order"] = form.severity_order.data or 0

            config["update"](item, **kwargs)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "drug_settings/form.html",
                form=form,
                dictionary_type=dictionary_type,
                config=config,
                item=item,
                mode="edit",
            )

        flash(f"{config['singular']} updated.", "success")
        return redirect(url_for("drug_settings.index"))

    return render_template(
        "drug_settings/form.html",
        form=form,
        dictionary_type=dictionary_type,
        config=config,
        item=item,
        mode="edit",
    )


@drug_settings_bp.post("/<dictionary_type>/<item_uuid>/deactivate")
@login_required
@RBACService.require_permission("drug_settings.manage")
def deactivate(dictionary_type, item_uuid):
    config = _get_config(dictionary_type)
    item = _get_item_or_404(config, item_uuid)

    DrugDictionaryService.deactivate_item(item)
    flash(f"{config['singular']} deactivated.", "success")

    return redirect(url_for("drug_settings.index"))


@drug_settings_bp.post("/<dictionary_type>/<item_uuid>/reactivate")
@login_required
@RBACService.require_permission("drug_settings.manage")
def reactivate(dictionary_type, item_uuid):
    config = _get_config(dictionary_type)
    item = _get_item_or_404(config, item_uuid)

    DrugDictionaryService.reactivate_item(item)
    flash(f"{config['singular']} reactivated.", "success")

    return redirect(url_for("drug_settings.index"))
