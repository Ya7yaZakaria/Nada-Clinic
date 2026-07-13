from datetime import date

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.forms.investigation_forms import InvestigationOrderForm, InvestigationOrderItemForm
from app.forms.investigation_preset_forms import InvestigationPresetApplyForm
from app.forms.investigation_result_forms import HistoricalInvestigationResultForm, InvestigationResultForm
from app.models import Patient, Visit
from app.models.investigation import InvestigationOrder, InvestigationOrderItem, InvestigationResult, InvestigationTest
from app.models.investigation_preset import InvestigationPreset
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_preset_service import InvestigationPresetService
from app.services.investigation_service import InvestigationService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.visit_service import VisitService


investigations_bp = Blueprint("investigations", __name__, url_prefix="/investigations")


def _test_choice_label(test):
    category_name = test.category.name_en if test.category else "Uncategorized"
    if test.default_unit:
        return f"{test.name_en} ({category_name}) — {test.default_unit}"
    return f"{test.name_en} ({category_name})"


def _populate_item_form(form):
    form.test_id.choices = [(0, "Select investigation test...")] + [
        (test.id, _test_choice_label(test))
        for test in InvestigationDictionaryService.list_active_tests()
    ]


def _populate_preset_apply_form(form):
    form.preset_id.choices = [(0, "Select investigation preset...")] + [
        (preset.id, preset.name)
        for preset in InvestigationPresetService.list_active_presets()
    ]


def _populate_abnormal_flag_choices(form):
    choices = [
        (InvestigationResult.FLAG_UNKNOWN, "Unknown"),
        (InvestigationResult.FLAG_NORMAL, "Normal"),
        (InvestigationResult.FLAG_LOW, "Low"),
        (InvestigationResult.FLAG_HIGH, "High"),
        (InvestigationResult.FLAG_ABNORMAL, "Abnormal"),
        (InvestigationResult.FLAG_CRITICAL, "Critical"),
        (InvestigationResult.FLAG_NOT_APPLICABLE, "Not applicable"),
    ]
    form.abnormal_flag.choices = choices


def _populate_historical_result_form(form):
    form.test_id.choices = [(0, "Select investigation test...")] + [
        (test.id, _test_choice_label(test))
        for test in InvestigationDictionaryService.list_active_tests()
    ]
    _populate_abnormal_flag_choices(form)


def _get_active_preset_or_none(preset_id):
    if not preset_id:
        return None
    return InvestigationPreset.query.filter_by(id=preset_id, is_active=True).first()


def _get_active_test_or_none(test_id):
    if not test_id:
        return None
    return InvestigationTest.query.filter_by(id=test_id, is_active=True).first()


def _apply_test_defaults_to_result_form(form, test):
    if not form.unit.data:
        form.unit.data = test.default_unit
    if not form.reference_range.data:
        form.reference_range.data = test.default_reference_range
    if not form.abnormal_flag.data:
        form.abnormal_flag.data = InvestigationResult.FLAG_UNKNOWN
    if not form.result_date.data:
        form.result_date.data = date.today()


@investigations_bp.get("/")
@login_required
@RBACService.require_permission("investigations.view")
def index():
    orders = (
        InvestigationOrder.query.order_by(
            InvestigationOrder.created_at.desc(),
            InvestigationOrder.id.desc(),
        )
        .limit(100)
        .all()
    )

    return render_template(
        "investigations/index.html",
        orders=orders,
        PatientService=PatientService,
    )


@investigations_bp.get("/patients/<patient_uuid>")
@login_required
@RBACService.require_permission("investigations.view")
def patient_orders(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()
    orders = (
        InvestigationOrder.query.filter_by(patient_id=patient.id)
        .order_by(InvestigationOrder.created_at.desc(), InvestigationOrder.id.desc())
        .all()
    )
    pending_items = InvestigationService.list_pending_order_items(patient)
    latest_results = InvestigationService.list_latest_results(patient)
    all_results = InvestigationService.list_results_for_patient(patient)

    can_manage_investigations = RBACService.user_has_permission(
        current_user,
        "investigations.manage",
    )

    return render_template(
        "investigations/patient_orders.html",
        patient=patient,
        orders=orders,
        pending_items=pending_items,
        latest_results=latest_results,
        all_results=all_results,
        can_manage_investigations=can_manage_investigations,
        PatientService=PatientService,
    )


@investigations_bp.route("/visits/<visit_uuid>/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("investigations.manage")
def new_from_visit(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()
    form = InvestigationOrderForm()

    if form.validate_on_submit():
        try:
            order = InvestigationService.create_order(
                patient=visit.patient,
                ordered_visit=visit,
                journey=visit.journey,
                priority=form.priority.data or InvestigationOrder.PRIORITY_ROUTINE,
                order_notes=form.order_notes.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "investigations/new_order.html",
                visit=visit,
                form=form,
                PatientService=PatientService,
            )

        flash("Investigation order created.", "success")
        return redirect(url_for("investigations.detail", order_uuid=order.uuid))

    return render_template(
        "investigations/new_order.html",
        visit=visit,
        form=form,
        PatientService=PatientService,
    )


@investigations_bp.get("/orders/<order_uuid>")
@login_required
@RBACService.require_permission("investigations.view")
def detail(order_uuid):
    order = InvestigationOrder.query.filter_by(uuid=order_uuid).first_or_404()
    items = (
        InvestigationOrderItem.query.filter_by(order_id=order.id)
        .order_by(InvestigationOrderItem.sort_order.asc(), InvestigationOrderItem.id.asc())
        .all()
    )

    results_by_item = {
        item.id: InvestigationService.list_results_for_order_item(item)
        for item in items
    }

    can_manage_investigations = RBACService.user_has_permission(
        current_user,
        "investigations.manage",
    )

    item_form = None
    preset_apply_form = None
    if can_manage_investigations:
        item_form = InvestigationOrderItemForm()
        _populate_item_form(item_form)
        preset_apply_form = InvestigationPresetApplyForm()
        _populate_preset_apply_form(preset_apply_form)

    return render_template(
        "investigations/detail.html",
        order=order,
        items=items,
        results_by_item=results_by_item,
        item_form=item_form,
        preset_apply_form=preset_apply_form,
        can_manage_investigations=can_manage_investigations,
        PatientService=PatientService,
        VisitService=VisitService,
    )


@investigations_bp.post("/orders/<order_uuid>/items")
@login_required
@RBACService.require_permission("investigations.manage")
def add_item(order_uuid):
    order = InvestigationOrder.query.filter_by(uuid=order_uuid).first_or_404()
    form = InvestigationOrderItemForm()
    _populate_item_form(form)

    if not form.validate_on_submit():
        flash("Invalid investigation item.", "danger")
        return redirect(url_for("investigations.detail", order_uuid=order.uuid))

    test = _get_active_test_or_none(form.test_id.data)

    try:
        InvestigationService.add_order_item(
            order=order,
            test=test,
            item_notes=form.item_notes.data,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("investigations.detail", order_uuid=order.uuid))

    flash("Investigation test added.", "success")
    return redirect(url_for("investigations.detail", order_uuid=order.uuid))


@investigations_bp.post("/orders/<order_uuid>/apply-preset")
@login_required
@RBACService.require_permission("investigations.manage")
def apply_preset(order_uuid):
    order = InvestigationOrder.query.filter_by(uuid=order_uuid).first_or_404()

    form = InvestigationPresetApplyForm()
    _populate_preset_apply_form(form)

    if not form.validate_on_submit():
        flash("Invalid investigation preset selection.", "danger")
        return redirect(url_for("investigations.detail", order_uuid=order.uuid))

    preset = _get_active_preset_or_none(form.preset_id.data)

    if not preset:
        flash("Investigation preset is required.", "danger")
        return redirect(url_for("investigations.detail", order_uuid=order.uuid))

    try:
        created_items = InvestigationPresetService.apply_to_order(
            preset=preset,
            order=order,
            actor_user=current_user,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("investigations.detail", order_uuid=order.uuid))

    flash(f"Investigation preset applied: {preset.name} ({len(created_items)} items).", "success")
    return redirect(url_for("investigations.detail", order_uuid=order.uuid))


@investigations_bp.route("/items/<item_uuid>/result/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("investigations.manage")
def new_result_for_item(item_uuid):
    item = InvestigationOrderItem.query.filter_by(uuid=item_uuid).first_or_404()
    form = InvestigationResultForm()
    _populate_abnormal_flag_choices(form)

    if form.validate_on_submit():
        try:
            InvestigationService.enter_result_for_order_item(
                order_item=item,
                result_visit=item.order.ordered_visit,
                result_date=form.result_date.data,
                lab_name=form.lab_name.data,
                result_value=form.result_value.data,
                unit=form.unit.data,
                reference_range=form.reference_range.data,
                result_text=form.result_text.data,
                doctor_comment=form.doctor_comment.data,
                abnormal_flag=form.abnormal_flag.data,
                has_attachment=form.has_attachment.data,
                attachment_label=form.attachment_label.data,
                external_report_reference=form.external_report_reference.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "investigations/result_form.html",
                form=form,
                item=item,
                order=item.order,
                mode="ordered",
                PatientService=PatientService,
            )

        flash("Investigation result entered.", "success")
        return redirect(url_for("investigations.detail", order_uuid=item.order.uuid))

    if form.is_submitted() is False:
        _apply_test_defaults_to_result_form(form, item.test)

    return render_template(
        "investigations/result_form.html",
        form=form,
        item=item,
        order=item.order,
        mode="ordered",
        PatientService=PatientService,
    )


@investigations_bp.route("/patients/<patient_uuid>/results/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("investigations.manage")
def new_historical_result_for_patient(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()
    form = HistoricalInvestigationResultForm()
    _populate_historical_result_form(form)

    if form.validate_on_submit():
        test = _get_active_test_or_none(form.test_id.data)

        try:
            InvestigationService.enter_historical_result(
                patient=patient,
                test=test,
                result_date=form.result_date.data,
                lab_name=form.lab_name.data,
                result_value=form.result_value.data,
                unit=form.unit.data,
                reference_range=form.reference_range.data,
                result_text=form.result_text.data,
                doctor_comment=form.doctor_comment.data,
                abnormal_flag=form.abnormal_flag.data,
                has_attachment=form.has_attachment.data,
                attachment_label=form.attachment_label.data,
                external_report_reference=form.external_report_reference.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "investigations/historical_result_form.html",
                form=form,
                patient=patient,
                visit=None,
                PatientService=PatientService,
            )

        flash("Historical investigation result entered.", "success")
        return redirect(url_for("investigations.patient_orders", patient_uuid=patient.uuid))

    if form.is_submitted() is False:
        form.result_date.data = date.today()
        form.abnormal_flag.data = InvestigationResult.FLAG_UNKNOWN

    return render_template(
        "investigations/historical_result_form.html",
        form=form,
        patient=patient,
        visit=None,
        PatientService=PatientService,
    )


@investigations_bp.route("/visits/<visit_uuid>/results/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("investigations.manage")
def new_historical_result_for_visit(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()
    patient = visit.patient
    form = HistoricalInvestigationResultForm()
    _populate_historical_result_form(form)

    if form.validate_on_submit():
        test = _get_active_test_or_none(form.test_id.data)

        try:
            InvestigationService.enter_historical_result(
                patient=patient,
                test=test,
                result_visit=visit,
                result_date=form.result_date.data,
                lab_name=form.lab_name.data,
                result_value=form.result_value.data,
                unit=form.unit.data,
                reference_range=form.reference_range.data,
                result_text=form.result_text.data,
                doctor_comment=form.doctor_comment.data,
                abnormal_flag=form.abnormal_flag.data,
                has_attachment=form.has_attachment.data,
                attachment_label=form.attachment_label.data,
                external_report_reference=form.external_report_reference.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "investigations/historical_result_form.html",
                form=form,
                patient=patient,
                visit=visit,
                PatientService=PatientService,
            )

        flash("Historical investigation result entered.", "success")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    if form.is_submitted() is False:
        form.result_date.data = date.today()
        form.abnormal_flag.data = InvestigationResult.FLAG_UNKNOWN

    return render_template(
        "investigations/historical_result_form.html",
        form=form,
        patient=patient,
        visit=visit,
        PatientService=PatientService,
    )


@investigations_bp.post("/items/<item_uuid>/cancel")
@login_required
@RBACService.require_permission("investigations.manage")
def cancel_item(item_uuid):
    item = InvestigationOrderItem.query.filter_by(uuid=item_uuid).first_or_404()
    order = item.order

    try:
        InvestigationService.cancel_order_item(item)
        InvestigationService._update_order_status_from_items(order)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("investigations.detail", order_uuid=order.uuid))

    flash("Investigation item cancelled.", "success")
    return redirect(url_for("investigations.detail", order_uuid=order.uuid))
