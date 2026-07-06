from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.forms.journey_forms import CloseJourneyForm, JourneyForm, ReopenJourneyForm
from app.models import Journey, Patient
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService

journeys_bp = Blueprint("journeys", __name__)


@journeys_bp.get("/patients/<patient_uuid>/journeys")
@login_required
@RBACService.require_permission("clinical.view")
def patient_journeys(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()
    journeys = JourneyService.get_patient_journeys(patient)

    return render_template(
        "journeys/index.html",
        patient=patient,
        journeys=journeys,
        JourneyService=JourneyService,
        PatientService=PatientService,
    )


@journeys_bp.route("/patients/<patient_uuid>/journeys/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("clinical.note.write")
def new(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()
    form = JourneyForm()

    if form.validate_on_submit():
        try:
            journey = JourneyService.create_journey(
                patient=patient,
                journey_type=form.journey_type.data,
                title=form.title.data,
                description=form.description.data,
                start_date=form.start_date.data,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "journeys/new.html",
                patient=patient,
                form=form,
                PatientService=PatientService,
            )

        flash("Journey created.", "success")
        return redirect(url_for("journeys.detail", journey_uuid=journey.uuid))

    return render_template(
        "journeys/new.html",
        patient=patient,
        form=form,
        PatientService=PatientService,
    )


@journeys_bp.get("/journeys/<journey_uuid>")
@login_required
@RBACService.require_permission("clinical.view")
def detail(journey_uuid):
    journey = Journey.query.filter_by(uuid=journey_uuid).first_or_404()

    return render_template(
        "journeys/detail.html",
        journey=journey,
        close_form=CloseJourneyForm(journey_type=journey.journey_type),
        reopen_form=ReopenJourneyForm(),
        JourneyService=JourneyService,
        PatientService=PatientService,
    )


@journeys_bp.route("/journeys/<journey_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("clinical.note.write")
def edit(journey_uuid):
    journey = Journey.query.filter_by(uuid=journey_uuid).first_or_404()
    form = JourneyForm(obj=journey)

    if form.validate_on_submit():
        try:
            JourneyService.update_journey(
                journey,
                journey_type=form.journey_type.data,
                title=form.title.data,
                description=form.description.data,
                start_date=form.start_date.data,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "journeys/edit.html",
                journey=journey,
                form=form,
                JourneyService=JourneyService,
                PatientService=PatientService,
            )

        flash("Journey updated.", "success")
        return redirect(url_for("journeys.detail", journey_uuid=journey.uuid))

    form.start_date.data = journey.start_date.isoformat()

    return render_template(
        "journeys/edit.html",
        journey=journey,
        form=form,
        JourneyService=JourneyService,
        PatientService=PatientService,
    )


@journeys_bp.post("/journeys/<journey_uuid>/close")
@login_required
@RBACService.require_permission("clinical.note.write")
def close(journey_uuid):
    journey = Journey.query.filter_by(uuid=journey_uuid).first_or_404()
    form = CloseJourneyForm(journey_type=journey.journey_type)

    if not form.validate_on_submit():
        flash("Journey closure was not confirmed or has invalid data.", "danger")
        return redirect(url_for("journeys.detail", journey_uuid=journey.uuid))

    try:
        JourneyService.close_journey(
            journey,
            outcome=form.outcome.data,
            end_date=form.end_date.data,
            outcome_note=form.outcome_note.data,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("journeys.detail", journey_uuid=journey.uuid))

    flash("Journey closed.", "warning")
    return redirect(url_for("journeys.detail", journey_uuid=journey.uuid))


@journeys_bp.post("/journeys/<journey_uuid>/reopen")
@login_required
@RBACService.require_permission("clinical.note.write")
def reopen(journey_uuid):
    journey = Journey.query.filter_by(uuid=journey_uuid).first_or_404()
    form = ReopenJourneyForm()

    if not form.validate_on_submit():
        flash("Journey reopening was not confirmed.", "danger")
        return redirect(url_for("journeys.detail", journey_uuid=journey.uuid))

    try:
        JourneyService.reopen_journey(journey)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("journeys.detail", journey_uuid=journey.uuid))

    flash("Journey reopened.", "success")
    return redirect(url_for("journeys.detail", journey_uuid=journey.uuid))
