from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.forms.visit_forms import VisitForm, VisitJourneyLinkForm
from app.models import Patient, Visit
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.visit_service import VisitService

visits_bp = Blueprint("visits", __name__)


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

    return render_template(
        "visits/detail.html",
        visit=visit,
        link_form=link_form,
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
