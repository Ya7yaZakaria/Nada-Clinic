import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.print_template_forms import PrintTemplateForm
from app.models.print_template import PrintTemplate
from app.services.print_template_service import PrintTemplateService
from app.services.rbac_service import RBACService


print_templates_bp = Blueprint(
    "print_templates",
    __name__,
    url_prefix="/print/templates",
)


def _document_type_label(document_type):
    labels = {
        PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION: "Prescription",
        PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST: "Investigation Request",
    }
    return labels.get(document_type, document_type)


def _apply_template_to_form(form, template):
    form.document_type.data = template.document_type
    form.name.data = template.name
    form.paper_width_mm.data = template.paper_width_mm
    form.paper_height_mm.data = template.paper_height_mm
    form.is_default.data = template.is_default
    form.is_active.data = template.is_active


@print_templates_bp.get("/")
@login_required
@RBACService.require_permission("print_templates.manage")
def index():
    templates = PrintTemplateService.list_all_templates()
    return render_template(
        "print_templates/index.html",
        templates=templates,
        document_type_label=_document_type_label,
    )


@print_templates_bp.post("/seed-defaults")
@login_required
@RBACService.require_permission("print_templates.manage")
def seed_defaults():
    PrintTemplateService.ensure_default_templates(actor_user=current_user)
    flash("Default print templates are ready.", "success")
    return redirect(url_for("print_templates.index"))


@print_templates_bp.route("/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("print_templates.manage")
def new():
    form = PrintTemplateForm()
    form.is_active.data = True if not form.is_submitted() else form.is_active.data
    form.paper_width_mm.data = form.paper_width_mm.data or PrintTemplateService.DEFAULT_PAPER_WIDTH_MM
    form.paper_height_mm.data = form.paper_height_mm.data or PrintTemplateService.DEFAULT_PAPER_HEIGHT_MM

    if form.validate_on_submit():
        try:
            template = PrintTemplateService.create_template(
                document_type=form.document_type.data,
                name=form.name.data,
                paper_width_mm=form.paper_width_mm.data,
                paper_height_mm=form.paper_height_mm.data,
                is_default=form.is_default.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("print_templates/form.html", form=form, mode="new")

        flash("Print template created.", "success")
        return redirect(url_for("print_templates.designer", template_uuid=template.uuid))

    return render_template("print_templates/form.html", form=form, mode="new")


@print_templates_bp.route("/<template_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("print_templates.manage")
def edit(template_uuid):
    template = PrintTemplate.query.filter_by(uuid=template_uuid).first_or_404()
    form = PrintTemplateForm()

    if form.validate_on_submit():
        try:
            PrintTemplateService.update_template(
                template,
                name=form.name.data,
                paper_width_mm=form.paper_width_mm.data,
                paper_height_mm=form.paper_height_mm.data,
                is_default=form.is_default.data,
                is_active=form.is_active.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "print_templates/form.html",
                form=form,
                mode="edit",
                template=template,
            )

        flash("Print template updated.", "success")
        return redirect(url_for("print_templates.designer", template_uuid=template.uuid))

    if form.is_submitted() is False:
        _apply_template_to_form(form, template)

    return render_template(
        "print_templates/form.html",
        form=form,
        mode="edit",
        template=template,
    )


@print_templates_bp.get("/<template_uuid>/designer")
@login_required
@RBACService.require_permission("print_templates.manage")
def designer(template_uuid):
    template = PrintTemplate.query.filter_by(uuid=template_uuid).first_or_404()

    return render_template(
        "print_templates/designer.html",
        template=template,
        document_type_label=_document_type_label,
    )


@print_templates_bp.post("/<template_uuid>/layout")
@login_required
@RBACService.require_permission("print_templates.manage")
def save_layout(template_uuid):
    template = PrintTemplate.query.filter_by(uuid=template_uuid).first_or_404()
    raw_layout = request.form.get("layout_json", "")

    try:
        layout_json = json.loads(raw_layout)
        PrintTemplateService.update_template(
            template,
            layout_json=layout_json,
            actor_user=current_user,
        )
    except json.JSONDecodeError:
        flash("Invalid layout JSON.", "danger")
        return redirect(url_for("print_templates.designer", template_uuid=template.uuid))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("print_templates.designer", template_uuid=template.uuid))

    flash("Print layout saved.", "success")
    return redirect(url_for("print_templates.designer", template_uuid=template.uuid))


@print_templates_bp.post("/<template_uuid>/deactivate")
@login_required
@RBACService.require_permission("print_templates.manage")
def deactivate(template_uuid):
    template = PrintTemplate.query.filter_by(uuid=template_uuid).first_or_404()
    PrintTemplateService.deactivate_template(template, actor_user=current_user)
    flash("Print template deactivated.", "success")
    return redirect(url_for("print_templates.index"))


@print_templates_bp.post("/<template_uuid>/reactivate")
@login_required
@RBACService.require_permission("print_templates.manage")
def reactivate(template_uuid):
    template = PrintTemplate.query.filter_by(uuid=template_uuid).first_or_404()
    PrintTemplateService.reactivate_template(template, actor_user=current_user)
    flash("Print template reactivated.", "success")
    return redirect(url_for("print_templates.index"))
