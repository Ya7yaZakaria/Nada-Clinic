import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.print_template_forms import PrintTemplateForm
from app.models import Visit
from app.models.print_template import PrintTemplate
from app.models.investigation import InvestigationOrder, InvestigationOrderItem
from app.services.patient_service import PatientService
from app.services.prescription_service import PrescriptionService
from app.services.print_template_service import PrintTemplateService
from app.services.rbac_service import RBACService


print_templates_bp = Blueprint(
    "print_templates",
    __name__,
    url_prefix="/print",
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


@print_templates_bp.get("/templates/")
@login_required
@RBACService.require_permission("print_templates.manage")
def index():
    templates = PrintTemplateService.list_all_templates()
    return render_template(
        "print_templates/index.html",
        templates=templates,
        document_type_label=_document_type_label,
    )


@print_templates_bp.post("/templates/seed-defaults")
@login_required
@RBACService.require_permission("print_templates.manage")
def seed_defaults():
    PrintTemplateService.ensure_default_templates(actor_user=current_user)
    flash("Default print templates are ready.", "success")
    return redirect(url_for("print_templates.index"))


@print_templates_bp.route("/templates/new", methods=["GET", "POST"])
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


@print_templates_bp.route("/templates/<template_uuid>/edit", methods=["GET", "POST"])
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


@print_templates_bp.get("/templates/<template_uuid>/designer")
@login_required
@RBACService.require_permission("print_templates.manage")
def designer(template_uuid):
    template = PrintTemplate.query.filter_by(uuid=template_uuid).first_or_404()

    return render_template(
        "print_templates/designer.html",
        template=template,
        document_type_label=_document_type_label,
    )


@print_templates_bp.post("/templates/<template_uuid>/layout")
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


def _prescription_line_text(item):
    drug = item.drug
    drug_parts = [
        getattr(drug, "trade_name", "") or "",
        getattr(drug, "strength", "") or "",
    ]
    drug_label = " ".join(part.strip() for part in drug_parts if part and part.strip())

    details = [
        item.dose,
        item.frequency,
        item.duration,
    ]

    if item.route:
        details.append(item.route.name_en)

    detail_label = " | ".join((value or "").strip() for value in details if value and value.strip())

    if item.instructions_ar:
        return f"{drug_label} - {detail_label} - {item.instructions_ar}"

    return f"{drug_label} - {detail_label}"


def _prescription_print_context_or_redirect(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()
    prescription = PrescriptionService.get_prescription_for_visit(visit)

    if not prescription:
        flash("No prescription exists for this visit.", "warning")
        return None, redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    prescription_items = PrescriptionService.list_items(prescription)
    if not prescription_items:
        flash("Prescription has no medications to print.", "warning")
        return None, redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    return (visit, prescription, prescription_items), None


def _get_prescription_template(template_uuid=None):
    if template_uuid:
        template = PrintTemplateService.get_template_by_uuid(template_uuid)
        if template and template.document_type == PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION:
            return template

    return PrintTemplateService.get_or_create_default_template(
        PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
        actor_user=current_user,
    )


@print_templates_bp.get("/prescriptions/<visit_uuid>/designer")
@login_required
@RBACService.require_permission("prescriptions.view")
def prescription_designer(visit_uuid):
    context, response = _prescription_print_context_or_redirect(visit_uuid)
    if response:
        return response

    template = _get_prescription_template()
    flash("Prescription uses the unified print template. Edit layout from Print Templates.", "info")
    return redirect(
        url_for(
            "print_templates.prescription_preview",
            visit_uuid=visit_uuid,
            template_uuid=template.uuid,
        )
    )


@print_templates_bp.get("/prescriptions/<visit_uuid>/preview")
@login_required
@RBACService.require_permission("prescriptions.view")
def prescription_preview(visit_uuid):
    context, response = _prescription_print_context_or_redirect(visit_uuid)
    if response:
        return response

    visit, prescription, prescription_items = context
    template = _get_prescription_template(request.args.get("template_uuid"))

    print_data = {
        "patient_name": PatientService.get_display_name(visit.patient),
        "mrn": visit.patient.formatted_mrn,
        "date": visit.visit_date.date().isoformat() if visit.visit_date else "",
        "prescription_items": [
            _prescription_line_text(item)
            for item in prescription_items
        ],
    }

    return render_template(
        "print_templates/prescription_preview.html",
        visit=visit,
        prescription=prescription,
        prescription_items=prescription_items,
        template=template,
        print_data=print_data,
        PatientService=PatientService,
    )


def _investigation_item_line_text(item):
    test = item.test
    parts = [test.name_en]

    if test.name_ar:
        parts.append(test.name_ar)

    if test.default_unit:
        parts.append(test.default_unit)

    line = " - ".join((part or "").strip() for part in parts if part and part.strip())

    if item.item_notes:
        line = f"{line} - {item.item_notes}"

    return line


def _investigation_print_context_or_redirect(order_uuid):
    order = InvestigationOrder.query.filter_by(uuid=order_uuid).first_or_404()
    items = (
        InvestigationOrderItem.query.filter_by(order_id=order.id)
        .filter(InvestigationOrderItem.status != InvestigationOrderItem.STATUS_CANCELLED)
        .order_by(InvestigationOrderItem.sort_order.asc(), InvestigationOrderItem.id.asc())
        .all()
    )

    if not items:
        flash("Investigation order has no tests to print.", "warning")
        return None, redirect(url_for("investigations.detail", order_uuid=order.uuid))

    return (order, items), None


def _get_investigation_template(template_uuid=None):
    if template_uuid:
        template = PrintTemplateService.get_template_by_uuid(template_uuid)
        if template and template.document_type == PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST:
            return template

    return PrintTemplateService.get_or_create_default_template(
        PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST,
        actor_user=current_user,
    )


@print_templates_bp.get("/investigations/<order_uuid>/designer")
@login_required
@RBACService.require_permission("investigations.view")
def investigation_designer(order_uuid):
    context, response = _investigation_print_context_or_redirect(order_uuid)
    if response:
        return response

    template = _get_investigation_template()
    flash("Investigation request uses the unified print template. Edit layout from Print Templates.", "info")
    return redirect(
        url_for(
            "print_templates.investigation_preview",
            order_uuid=order_uuid,
            template_uuid=template.uuid,
        )
    )


@print_templates_bp.get("/investigations/<order_uuid>/preview")
@login_required
@RBACService.require_permission("investigations.view")
def investigation_preview(order_uuid):
    context, response = _investigation_print_context_or_redirect(order_uuid)
    if response:
        return response

    order, items = context
    template = _get_investigation_template(request.args.get("template_uuid"))

    instruction_element = (template.layout_json or {}).get("instruction", {})
    default_instruction = instruction_element.get("defaultText") or ""

    print_data = {
        "patient_name": PatientService.get_display_name(order.patient),
        "mrn": order.patient.formatted_mrn,
        "date": order.created_at.date().isoformat() if order.created_at else "",
        "instruction": default_instruction,
        "investigation_items": [
            _investigation_item_line_text(item)
            for item in items
        ],
    }

    return render_template(
        "print_templates/investigation_request_preview.html",
        order=order,
        items=items,
        template=template,
        print_data=print_data,
        PatientService=PatientService,
    )


@print_templates_bp.post("/templates/<template_uuid>/deactivate")
@login_required
@RBACService.require_permission("print_templates.manage")
def deactivate(template_uuid):
    template = PrintTemplate.query.filter_by(uuid=template_uuid).first_or_404()
    PrintTemplateService.deactivate_template(template, actor_user=current_user)
    flash("Print template deactivated.", "success")
    return redirect(url_for("print_templates.index"))


@print_templates_bp.post("/templates/<template_uuid>/reactivate")
@login_required
@RBACService.require_permission("print_templates.manage")
def reactivate(template_uuid):
    template = PrintTemplate.query.filter_by(uuid=template_uuid).first_or_404()
    PrintTemplateService.reactivate_template(template, actor_user=current_user)
    flash("Print template reactivated.", "success")
    return redirect(url_for("print_templates.index"))
