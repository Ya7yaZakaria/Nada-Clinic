from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.investigation_forms import InvestigationOrderItemForm
from app.forms.prescription_forms import PrescriptionItemForm
from app.forms.prescription_preset_forms import PrescriptionPresetApplyForm
from app.forms.ultrasound_forms import (
    ClinicUltrasoundForm,
    ExternalUltrasoundRequestForm,
    ExternalUltrasoundResultForm,
)
from app.forms.visit_forms import VisitForm, VisitJourneyLinkForm
from app.models import ClinicUltrasoundExam, Patient, Visit
from app.models.drug import Drug
from app.models.drug_dictionary import DrugRoute
from app.models.investigation import InvestigationOrder, InvestigationOrderItem
from app.models.prescription import PrescriptionItem
from app.models.prescription_preset import PrescriptionPreset
from app.services.clinic_ultrasound_service import ClinicUltrasoundService
from app.services.drug_dictionary_service import DrugDictionaryService
from app.services.drug_service import DrugService
from app.services.external_ultrasound_service import ExternalUltrasoundService
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_service import InvestigationService
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.prescription_service import PrescriptionService
from app.services.prescription_preset_service import PrescriptionPresetService
from app.services.rbac_service import RBACService
from app.services.visit_service import VisitService

visits_bp = Blueprint("visits", __name__)


def _choice_label(item):
    if getattr(item, "name_ar", None):
        return f"{item.name_en} / {item.name_ar}"
    return item.name_en


def _drug_choice_label(drug):
    form_name = drug.form.name_en if drug.form else "-"
    return f"{drug.trade_name} {drug.strength} - {drug.generic_name} ({form_name})"


def _populate_prescription_item_form(form):
    form.drug_id.choices = [(0, "Select drug...")] + [
        (drug.id, _drug_choice_label(drug))
        for drug in DrugService.get_active_drugs()
    ]
    form.route_id.choices = [(0, "Use drug default route")] + [
        (route.id, _choice_label(route))
        for route in DrugDictionaryService.get_active_routes()
    ]


def _populate_prescription_preset_apply_form(form):
    form.preset_id.choices = [(0, "Select preset...")] + [
        (preset.id, preset.name)
        for preset in PrescriptionPresetService.list_active_presets()
    ]



def _investigation_test_choice_label(test):
    category_name = test.category.name_en if test.category else "Uncategorized"
    if test.default_unit:
        return f"{test.name_en} ({category_name}) - {test.default_unit}"
    return f"{test.name_en} ({category_name})"


def _populate_investigation_item_form(form):
    form.test_id.choices = [(0, "Select investigation test...")] + [
        (test.id, _investigation_test_choice_label(test))
        for test in InvestigationDictionaryService.list_active_tests()
    ]

def _get_drug_or_none(drug_id):
    if not drug_id:
        return None
    return Drug.query.filter_by(id=drug_id, is_active=True).first()


def _get_route_or_none(route_id):
    if not route_id:
        return None
    return DrugRoute.query.filter_by(id=route_id, is_active=True).first()


def _apply_item_to_form(form, item):
    form.drug_id.data = item.drug_id
    form.route_id.data = item.route_id or 0
    form.dose.data = item.dose
    form.frequency.data = item.frequency
    form.duration.data = item.duration
    form.instructions_ar.data = item.instructions_ar


def _parse_follow_up_date(value):
    cleaned = (value or "").strip()

    if not cleaned:
        return None

    return datetime.strptime(cleaned, "%Y-%m-%d").date()


@visits_bp.route("/patients/<patient_uuid>/visits/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("clinical.note.write")
def new(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()
    journeys = VisitService.get_available_journeys(patient)
    active_journeys = JourneyService.get_active_journeys(patient)

    form = VisitForm()
    form.set_journey_choices(journeys)

    if len(active_journeys) == 1 and not form.journey_id.data:
        form.journey_id.data = str(active_journeys[0].id)

    if form.validate_on_submit():
        try:
            visit = VisitService.create_visit(
                patient=patient,
                journey_id=form.journey_id.data or None,
                visit_type=form.visit_type.data,
                chief_complaint=form.chief_complaint.data,
                history=form.history.data,
                examination=form.examination.data,
                assessment=form.assessment.data,
                plan=form.plan.data,
                follow_up_date=_parse_follow_up_date(form.follow_up_date.data),
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "visits/new.html",
                patient=patient,
                form=form,
                PatientService=PatientService,
            )

        if VisitService.has_unassigned_warning(visit):
            flash("Visit created. Warning: this visit is not linked to any Journey.", "warning")
        else:
            flash("Visit created.", "success")

        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    return render_template(
        "visits/new.html",
        patient=patient,
        form=form,
        PatientService=PatientService,
    )


@visits_bp.get("/visits/<visit_uuid>")
@login_required
@RBACService.require_permission("clinical.view")
def detail(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()
    journeys = VisitService.get_available_journeys(visit.patient)
    link_form = VisitJourneyLinkForm()
    link_form.set_journey_choices(journeys)
    link_form.journey_id.data = str(visit.journey_id) if visit.journey_id else ""

    can_view_prescription = RBACService.user_has_permission(current_user, "prescriptions.view")
    can_manage_prescription = RBACService.user_has_permission(current_user, "prescriptions.manage")
    can_view_investigations = RBACService.user_has_permission(current_user, "investigations.view")
    can_manage_investigations = RBACService.user_has_permission(current_user, "investigations.manage")
    can_view_ultrasounds = RBACService.user_has_permission(current_user, "ultrasound.view")
    can_manage_ultrasounds = RBACService.user_has_permission(current_user, "ultrasound.manage")

    prescription = None
    prescription_items = []
    prescription_item_form = None
    prescription_preset_apply_form = None

    investigation_orders = []
    investigation_pending_items = []
    patient_pending_investigation_items = []
    investigation_item_form = None

    clinic_ultrasound_exams = []
    ultrasound_form = None
    ultrasound_edit_exam = None
    ultrasound_edit_form = None
    external_ultrasound_pending_requests = []
    external_ultrasound_results = []
    external_ultrasound_request_form = None
    external_ultrasound_result_form = None

    if can_view_prescription:
        prescription = PrescriptionService.get_prescription_for_visit(visit)
        if prescription:
            prescription_items = PrescriptionService.list_items(prescription)

    if can_manage_prescription:
        prescription_item_form = PrescriptionItemForm()
        _populate_prescription_item_form(prescription_item_form)
        prescription_preset_apply_form = PrescriptionPresetApplyForm()
        _populate_prescription_preset_apply_form(prescription_preset_apply_form)

    if can_view_investigations:
        investigation_orders = (
            InvestigationOrder.query.filter_by(ordered_visit_id=visit.id)
            .order_by(InvestigationOrder.created_at.desc(), InvestigationOrder.id.desc())
            .all()
        )
        investigation_pending_items = (
            InvestigationOrderItem.query.join(InvestigationOrder)
            .filter(InvestigationOrder.ordered_visit_id == visit.id)
            .filter(
                InvestigationOrderItem.status.in_(
                    [
                        InvestigationOrderItem.STATUS_ORDERED,
                        InvestigationOrderItem.STATUS_PENDING_RESULT,
                    ]
                )
            )
            .order_by(InvestigationOrder.created_at.asc(), InvestigationOrderItem.sort_order.asc())
            .all()
        )

        patient_pending_investigation_items = [
            item
            for item in InvestigationService.list_pending_order_items(visit.patient)
            if item.order.ordered_visit_id != visit.id
        ]

    if can_manage_investigations:
        investigation_item_form = InvestigationOrderItemForm()
        _populate_investigation_item_form(investigation_item_form)

    if can_view_ultrasounds:
        clinic_ultrasound_exams = ClinicUltrasoundService.list_visit_exams(visit)
        external_ultrasound_pending_requests = ExternalUltrasoundService.list_pending_for_patient(visit.patient)
        external_ultrasound_results = ExternalUltrasoundService.list_visit_results(visit)

    if can_manage_ultrasounds:
        ultrasound_form = ClinicUltrasoundForm()
        external_ultrasound_request_form = ExternalUltrasoundRequestForm()
        external_ultrasound_result_form = ExternalUltrasoundResultForm()
        external_ultrasound_result_form.set_request_choices(external_ultrasound_pending_requests)
        edit_ultrasound_uuid = request.args.get("edit_ultrasound")
        if edit_ultrasound_uuid:
            candidate = ClinicUltrasoundService.get_exam(edit_ultrasound_uuid)
            if candidate and candidate.visit_id == visit.id:
                ultrasound_edit_exam = candidate
                ultrasound_edit_form = ClinicUltrasoundForm()
                ultrasound_edit_form.apply_exam(candidate)

    return render_template(
        "visits/detail.html",
        visit=visit,
        link_form=link_form,
        prescription=prescription,
        prescription_items=prescription_items,
        prescription_item_form=prescription_item_form,
        prescription_preset_apply_form=prescription_preset_apply_form,
        can_view_prescription=can_view_prescription,
        can_manage_prescription=can_manage_prescription,
        investigation_orders=investigation_orders,
        investigation_pending_items=investigation_pending_items,
        patient_pending_investigation_items=patient_pending_investigation_items,
        investigation_item_form=investigation_item_form,
        can_view_investigations=can_view_investigations,
        can_manage_investigations=can_manage_investigations,
        clinic_ultrasound_exams=clinic_ultrasound_exams,
        ultrasound_form=ultrasound_form,
        ultrasound_edit_exam=ultrasound_edit_exam,
        ultrasound_edit_form=ultrasound_edit_form,
        can_view_ultrasounds=can_view_ultrasounds,
        can_manage_ultrasounds=can_manage_ultrasounds,
        external_ultrasound_pending_requests=external_ultrasound_pending_requests,
        external_ultrasound_results=external_ultrasound_results,
        external_ultrasound_request_form=external_ultrasound_request_form,
        external_ultrasound_result_form=external_ultrasound_result_form,
        ClinicUltrasoundService=ClinicUltrasoundService,
        JourneyService=JourneyService,
        PatientService=PatientService,
        VisitService=VisitService,
    )


@visits_bp.route("/visits/<visit_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("clinical.note.write")
def edit(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()
    journeys = VisitService.get_available_journeys(visit.patient)

    form = VisitForm(obj=visit)
    form.set_journey_choices(journeys)

    if visit.journey_id and not form.journey_id.data:
        form.journey_id.data = str(visit.journey_id)

    if form.validate_on_submit():
        try:
            VisitService.update_visit(
                visit,
                journey_id=form.journey_id.data or None,
                visit_type=form.visit_type.data,
                chief_complaint=form.chief_complaint.data,
                history=form.history.data,
                examination=form.examination.data,
                assessment=form.assessment.data,
                plan=form.plan.data,
                follow_up_date=_parse_follow_up_date(form.follow_up_date.data),
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "visits/edit.html",
                visit=visit,
                form=form,
                PatientService=PatientService,
            )

        if VisitService.has_unassigned_warning(visit):
            flash("Visit updated. Warning: this visit is not linked to any Journey.", "warning")
        else:
            flash("Visit updated.", "success")

        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    if visit.follow_up_date:
        form.follow_up_date.data = visit.follow_up_date.isoformat()

    return render_template(
        "visits/edit.html",
        visit=visit,
        form=form,
        PatientService=PatientService,
    )


@visits_bp.post("/visits/<visit_uuid>/journey")
@login_required
@RBACService.require_permission("clinical.note.write")
def update_journey_link(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()
    journeys = VisitService.get_available_journeys(visit.patient)

    form = VisitJourneyLinkForm()
    form.set_journey_choices(journeys)

    if not form.validate_on_submit():
        flash("Invalid journey selection.", "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    try:
        VisitService.assign_journey(visit, form.journey_id.data or None)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    if VisitService.has_unassigned_warning(visit):
        flash("Journey link removed. Warning: this visit is standalone.", "warning")
    else:
        flash("Journey link updated.", "success")

    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))


@visits_bp.post("/visits/<visit_uuid>/prescription/items")
@login_required
@RBACService.require_permission("prescriptions.manage")
def add_prescription_item(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()
    form = PrescriptionItemForm()
    _populate_prescription_item_form(form)

    if not form.validate_on_submit():
        flash("Invalid prescription item.", "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    drug = _get_drug_or_none(form.drug_id.data)
    route = _get_route_or_none(form.route_id.data)

    try:
        prescription = PrescriptionService.get_or_create_prescription(
            visit=visit,
            actor_user=current_user,
        )
        PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose=form.dose.data,
            frequency=form.frequency.data,
            duration=form.duration.data,
            instructions_ar=form.instructions_ar.data,
            route=route,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    flash("Medication added to prescription.", "success")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))


@visits_bp.post("/visits/<visit_uuid>/prescription/apply-preset")
@login_required
@RBACService.require_permission("prescriptions.manage")
def apply_prescription_preset(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()

    form = PrescriptionPresetApplyForm()
    _populate_prescription_preset_apply_form(form)

    if not form.validate_on_submit():
        flash("Invalid prescription preset selection.", "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    preset = PrescriptionPreset.query.filter_by(
        id=form.preset_id.data,
        is_active=True,
    ).first()

    if not preset:
        flash("Prescription preset is required.", "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    try:
        prescription = PrescriptionService.get_or_create_prescription(
            visit=visit,
            actor_user=current_user,
        )
        created_items = PrescriptionPresetService.apply_to_prescription(
            preset=preset,
            prescription=prescription,
            actor_user=current_user,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    flash(f"Prescription preset applied: {preset.name} ({len(created_items)} items).", "success")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))


@visits_bp.route("/prescription-items/<item_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("prescriptions.manage")
def edit_prescription_item(item_uuid):
    item = PrescriptionItem.query.filter_by(uuid=item_uuid).first_or_404()
    visit = item.prescription.visit

    form = PrescriptionItemForm()
    _populate_prescription_item_form(form)

    if form.validate_on_submit():
        drug = _get_drug_or_none(form.drug_id.data)
        route = _get_route_or_none(form.route_id.data)

        try:
            PrescriptionService.update_item(
                item,
                drug=drug,
                dose=form.dose.data,
                frequency=form.frequency.data,
                duration=form.duration.data,
                instructions_ar=form.instructions_ar.data,
                route=route,
            )
            PrescriptionService.update_prescription(
                item.prescription,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "visits/prescription_item_form.html",
                form=form,
                item=item,
                visit=visit,
            )

        flash("Medication updated.", "success")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    if item.drug_id and not form.drug_id.data:
        _apply_item_to_form(form, item)

    return render_template(
        "visits/prescription_item_form.html",
        form=form,
        item=item,
        visit=visit,
    )


@visits_bp.post("/prescription-items/<item_uuid>/remove")
@login_required
@RBACService.require_permission("prescriptions.manage")
def remove_prescription_item(item_uuid):
    item = PrescriptionItem.query.filter_by(uuid=item_uuid).first_or_404()
    visit = item.prescription.visit

    PrescriptionService.remove_item(item)

    flash("Medication removed from prescription.", "success")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))
