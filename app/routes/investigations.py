from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.forms.investigation_forms import InvestigationOrderForm, InvestigationOrderItemForm
from app.models import Patient, Visit
from app.models.investigation import InvestigationOrder, InvestigationOrderItem, InvestigationTest
from app.services.investigation_dictionary_service import InvestigationDictionaryService
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


def _get_active_test_or_none(test_id):
    if not test_id:
        return None
    return InvestigationTest.query.filter_by(id=test_id, is_active=True).first()


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

    return render_template(
        "investigations/patient_orders.html",
        patient=patient,
        orders=orders,
        pending_items=pending_items,
        latest_results=latest_results,
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

    can_manage_investigations = RBACService.user_has_permission(
        current_user,
        "investigations.manage",
    )

    item_form = None
    if can_manage_investigations:
        item_form = InvestigationOrderItemForm()
        _populate_item_form(item_form)

    return render_template(
        "investigations/detail.html",
        order=order,
        items=items,
        item_form=item_form,
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
