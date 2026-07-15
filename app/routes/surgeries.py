from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.surgery_forms import SurgeryCancelForm, SurgeryCompleteForm, SurgeryForm, SurgeryPostponeForm
from app.models import Patient, Visit
from app.models.surgery import SurgeryCase
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.surgery_analytics_service import SurgeryAnalyticsService
from app.services.surgery_service import SurgeryService

surgeries_bp = Blueprint("surgeries", __name__, url_prefix="/surgeries")


def _patient_choice_label(patient):
    name = PatientService.get_display_name(patient)
    return f"{name} — {patient.phone_primary}"


def _patient_choices():
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.created_at.desc()).limit(100).all()
    return [(0, "Select patient...")] + [(patient.id, _patient_choice_label(patient)) for patient in patients]


def _get_patient(patient_id):
    if not patient_id:
        return None
    return Patient.query.filter_by(id=patient_id, is_active=True).first()


def _apply_form_to_service(form, patient, source_visit=None, surgery=None):
    kwargs = {
        "procedure_name": form.procedure_name.data,
        "procedure_category": form.procedure_category.data,
        "scheduled_at": form.scheduled_at(),
        "location": form.location.data,
        "priority": form.priority.data,
        "pre_op_note": form.pre_op_note.data,
        "surgery_note": form.surgery_note.data,
        "fee_amount": form.fee_amount.data,
        "paid_amount": form.paid_amount.data,
        "payment_status": form.payment_status.data,
    }

    if surgery:
        return SurgeryService.update_surgery(surgery, **kwargs)

    return SurgeryService.create_surgery(
        patient=patient,
        source_visit=source_visit,
        actor_user=current_user,
        **kwargs,
    )


@surgeries_bp.get("/")
@login_required
@RBACService.require_permission("surgeries.view")
def index():
    today_surgeries = SurgeryService.list_today_surgeries()
    upcoming_surgeries = SurgeryService.list_upcoming_surgeries(limit=10)
    recent_completed = SurgeryService.list_recent_completed(limit=10)
    postponed_cancelled_surgeries = SurgeryService.list_by_statuses(
        [
            SurgeryCase.STATUS_POSTPONED,
            SurgeryCase.STATUS_CANCELLED,
        ],
        limit=10,
    )

    return render_template(
        "surgeries/index.html",
        today_surgeries=today_surgeries,
        upcoming_surgeries=upcoming_surgeries,
        recent_completed=recent_completed,
        postponed_cancelled_surgeries=postponed_cancelled_surgeries,
        SurgeryService=SurgeryService,
    )


@surgeries_bp.get("/list")
@login_required
@RBACService.require_permission("surgeries.view")
def list_view():
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    status = request.args.get("status") or None
    category = request.args.get("category") or None
    patient_query = request.args.get("patient") or None

    parsed_from = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
    parsed_to = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None

    surgeries = SurgeryService.list_by_date_range(
        date_from=parsed_from,
        date_to=parsed_to,
        status=status,
        category=category,
        patient_query=patient_query,
    )

    return render_template(
        "surgeries/list.html",
        surgeries=surgeries,
        SurgeryService=SurgeryService,
        SurgeryCase=SurgeryCase,
    )


@surgeries_bp.get("/calendar")
@login_required
@RBACService.require_permission("surgeries.view")
def calendar():
    surgeries = SurgeryService.list_by_date_range()
    grouped = {}
    for surgery in surgeries:
        grouped.setdefault(surgery.scheduled_at.date(), []).append(surgery)

    return render_template(
        "surgeries/calendar.html",
        grouped_surgeries=grouped,
        SurgeryService=SurgeryService,
    )


@surgeries_bp.route("/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("surgeries.manage")
def new():
    form = SurgeryForm()
    form.set_choices(_patient_choices())

    if form.validate_on_submit():
        patient = _get_patient(form.patient_id.data)
        try:
            surgery = _apply_form_to_service(form, patient)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("surgeries/new.html", form=form, patient=None)

        flash("Surgery scheduled.", "success")
        return redirect(url_for("surgeries.detail", surgery_uuid=surgery.uuid))

    return render_template("surgeries/new.html", form=form, patient=None)


@surgeries_bp.route("/patient/<patient_uuid>/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("surgeries.manage")
def new_for_patient(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid, is_active=True).first_or_404()
    form = SurgeryForm()
    form.set_choices([(patient.id, _patient_choice_label(patient))])
    form.patient_id.data = patient.id

    if form.validate_on_submit():
        try:
            surgery = _apply_form_to_service(form, patient)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("surgeries/new.html", form=form, patient=patient)

        flash("Surgery scheduled.", "success")
        return redirect(url_for("surgeries.detail", surgery_uuid=surgery.uuid))

    return render_template("surgeries/new.html", form=form, patient=patient)


@surgeries_bp.route("/visit/<visit_uuid>/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("surgeries.manage")
def new_for_visit(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()
    patient = visit.patient
    form = SurgeryForm()
    form.set_choices([(patient.id, _patient_choice_label(patient))])
    form.patient_id.data = patient.id

    if form.validate_on_submit():
        try:
            surgery = _apply_form_to_service(form, patient, source_visit=visit)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("surgeries/new.html", form=form, patient=patient, visit=visit)

        flash("Surgery scheduled from visit.", "success")
        return redirect(url_for("surgeries.detail", surgery_uuid=surgery.uuid))

    return render_template("surgeries/new.html", form=form, patient=patient, visit=visit)


@surgeries_bp.get("/insights")
@login_required
@RBACService.require_permission("surgeries.view")
def insights():
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    parsed_from = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
    parsed_to = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None
    summary = SurgeryAnalyticsService.summarize_by_date_range(parsed_from, parsed_to)

    return render_template(
        "surgeries/insights.html",
        summary=summary,
        SurgeryService=SurgeryService,
    )


@surgeries_bp.get("/<surgery_uuid>")
@login_required
@RBACService.require_permission("surgeries.view")
def detail(surgery_uuid):
    surgery = SurgeryService.get_surgery(surgery_uuid)
    if not surgery:
        flash("Surgery not found.", "danger")
        return redirect(url_for("surgeries.index"))

    return render_template(
        "surgeries/detail.html",
        surgery=surgery,
        SurgeryService=SurgeryService,
    )


@surgeries_bp.route("/<surgery_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("surgeries.manage")
def edit(surgery_uuid):
    surgery = SurgeryService.get_surgery(surgery_uuid)
    if not surgery:
        flash("Surgery not found.", "danger")
        return redirect(url_for("surgeries.index"))

    form = SurgeryForm()
    form.set_choices([(surgery.patient_id, _patient_choice_label(surgery.patient))])

    if request.method == "GET":
        form.patient_id.data = surgery.patient_id
        form.apply_surgery(surgery)

    if form.validate_on_submit():
        try:
            SurgeryService.update_surgery(
                surgery,
                procedure_name=form.procedure_name.data,
                procedure_category=form.procedure_category.data,
                scheduled_at=form.scheduled_at(),
                location=form.location.data,
                priority=form.priority.data,
                pre_op_note=form.pre_op_note.data,
                surgery_note=form.surgery_note.data,
                fee_amount=form.fee_amount.data,
                paid_amount=form.paid_amount.data,
                payment_status=form.payment_status.data,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("surgeries/new.html", form=form, patient=surgery.patient, surgery=surgery)

        flash("Surgery updated.", "success")
        return redirect(url_for("surgeries.detail", surgery_uuid=surgery.uuid))

    return render_template("surgeries/new.html", form=form, patient=surgery.patient, surgery=surgery)


@surgeries_bp.route("/<surgery_uuid>/complete", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("surgeries.manage")
def complete(surgery_uuid):
    surgery = SurgeryService.get_surgery(surgery_uuid)
    if not surgery:
        flash("Surgery not found.", "danger")
        return redirect(url_for("surgeries.index"))

    form = SurgeryCompleteForm()
    form.set_choices()

    if request.method == "GET":
        form.completed_date.data = datetime.now().date()
        form.completed_time.data = datetime.now().time().replace(second=0, microsecond=0)
        form.fee_amount.data = surgery.fee_amount
        form.paid_amount.data = surgery.paid_amount
        form.payment_status.data = ""

    if form.validate_on_submit():
        try:
            SurgeryService.complete_surgery(
                surgery,
                completed_at=form.completed_at(),
                operative_findings=form.operative_findings.data,
                operative_details=form.operative_details.data,
                complications=form.complications.data,
                post_op_plan=form.post_op_plan.data,
                fee_amount=form.fee_amount.data,
                paid_amount=form.paid_amount.data,
                payment_status=form.payment_status.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("surgeries/complete.html", surgery=surgery, form=form)

        flash("Surgery completed.", "success")
        return redirect(url_for("surgeries.detail", surgery_uuid=surgery.uuid))

    return render_template("surgeries/complete.html", surgery=surgery, form=form)


@surgeries_bp.route("/<surgery_uuid>/cancel", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("surgeries.manage")
def cancel(surgery_uuid):
    surgery = SurgeryService.get_surgery(surgery_uuid)
    if not surgery:
        flash("Surgery not found.", "danger")
        return redirect(url_for("surgeries.index"))

    form = SurgeryCancelForm()

    if form.validate_on_submit():
        try:
            SurgeryService.cancel_surgery(
                surgery,
                cancel_reason=form.cancel_reason.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("surgeries/cancel.html", surgery=surgery, form=form)

        flash("Surgery cancelled.", "success")
        return redirect(url_for("surgeries.detail", surgery_uuid=surgery.uuid))

    return render_template("surgeries/cancel.html", surgery=surgery, form=form)


@surgeries_bp.post("/<surgery_uuid>/mark-scheduled")
@login_required
@RBACService.require_permission("surgeries.manage")
def mark_scheduled(surgery_uuid):
    surgery = SurgeryService.get_surgery(surgery_uuid)
    if not surgery:
        flash("Surgery not found.", "danger")
        return redirect(url_for("surgeries.index"))

    try:
        SurgeryService.mark_postponed_as_scheduled(surgery)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("surgeries.detail", surgery_uuid=surgery.uuid))

    flash("Surgery marked as scheduled.", "success")
    return redirect(url_for("surgeries.detail", surgery_uuid=surgery.uuid))


@surgeries_bp.route("/<surgery_uuid>/postpone", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("surgeries.manage")
def postpone(surgery_uuid):
    surgery = SurgeryService.get_surgery(surgery_uuid)
    if not surgery:
        flash("Surgery not found.", "danger")
        return redirect(url_for("surgeries.index"))

    form = SurgeryPostponeForm()

    if request.method == "GET":
        form.new_scheduled_date.data = surgery.scheduled_at.date()
        form.new_scheduled_time.data = surgery.scheduled_at.time().replace(second=0, microsecond=0)

    if form.validate_on_submit():
        try:
            SurgeryService.postpone_surgery(
                surgery,
                new_scheduled_at=form.new_scheduled_at(),
                postponed_reason=form.postponed_reason.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("surgeries/postpone.html", surgery=surgery, form=form)

        flash("Surgery postponed.", "success")
        return redirect(url_for("surgeries.detail", surgery_uuid=surgery.uuid))

    return render_template("surgeries/postpone.html", surgery=surgery, form=form)
