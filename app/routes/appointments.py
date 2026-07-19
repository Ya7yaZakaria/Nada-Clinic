from calendar import Calendar, month_name
from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.appointment_forms import (
    AppointmentArriveForm,
    AppointmentCancelForm,
    AppointmentForm,
    AppointmentRescheduleForm,
)
from app.models import Patient
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService

appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


def _parse_date(value, fallback=None):
    if not value:
        return fallback or date.today()

    try:
        return date.fromisoformat(value)
    except ValueError:
        return fallback or date.today()


def _month_bounds(year, month):
    first_day = date(year, month, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    return first_day, next_month - timedelta(days=1)


def _week_bounds(selected_date):
    start = selected_date - timedelta(days=selected_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def _build_month_weeks(year, month):
    calendar = Calendar(firstweekday=0)
    return calendar.monthdatescalendar(year, month)


def _get_patient_from_form(form):
    patient_id = form.patient_id.data

    if not patient_id:
        return None

    return db.session.get(Patient, int(patient_id))


@appointments_bp.get("/")
@login_required
@RBACService.require_permission("appointments.view")
def index():
    selected_date = _parse_date(request.args.get("date"))
    appointments = AppointmentService.get_appointments_for_date(selected_date)

    return render_template(
        "appointments/index.html",
        appointments=appointments,
        selected_date=selected_date,
        AppointmentService=AppointmentService,
        PatientService=PatientService,
    )


@appointments_bp.get("/calendar")
@login_required
@RBACService.require_permission("appointments.view")
def calendar():
    selected_date = _parse_date(request.args.get("date"))
    view = request.args.get("view", "month")

    if view not in {"month", "week", "day"}:
        view = "month"

    month_start, month_end = _month_bounds(selected_date.year, selected_date.month)
    week_start, week_end = _week_bounds(selected_date)

    if view == "week":
        appointments = AppointmentService.get_appointments_between_dates(week_start, week_end)
    elif view == "day":
        appointments = AppointmentService.get_appointments_for_date(selected_date)
    else:
        appointments = AppointmentService.get_appointments_between_dates(month_start, month_end)

    month_counts = AppointmentService.get_calendar_counts(month_start, month_end)
    selected_day_appointments = AppointmentService.get_appointments_for_date(selected_date)

    previous_month_date = month_start - timedelta(days=1)
    next_month_date = month_end + timedelta(days=1)

    return render_template(
        "appointments/calendar.html",
        view=view,
        selected_date=selected_date,
        today=date.today(),
        month_name=month_name[selected_date.month],
        month_weeks=_build_month_weeks(selected_date.year, selected_date.month),
        month_counts=month_counts,
        appointments=appointments,
        selected_day_appointments=selected_day_appointments,
        week_start=week_start,
        week_end=week_end,
        previous_month_date=previous_month_date,
        next_month_date=next_month_date,
        AppointmentService=AppointmentService,
        PatientService=PatientService,
    )


@appointments_bp.route("/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("appointments.manage")
def new():
    patient_uuid = request.args.get("patient_uuid")
    patient = Patient.query.filter_by(uuid=patient_uuid).first() if patient_uuid else None
    patient_query = request.args.get("q", "")
    patients = PatientService.search_patients(patient_query, limit=10) if patient_query else []

    form = AppointmentForm()

    if patient and request.method == "GET":
        form.patient_id.data = str(patient.id)

    if form.validate_on_submit():
        patient = _get_patient_from_form(form)

        if not patient:
            flash("Please select a patient.", "danger")
            return render_template(
                "appointments/new.html",
                form=form,
                patient=None,
                patients=patients,
                patient_query=patient_query,
            )

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
            duration_minutes=form.duration_minutes.data,
            appointment_type=form.appointment_type.data,
            source=form.source.data,
            notes=form.notes.data,
            fee_amount=form.fee_amount.data,
            paid_amount=form.paid_amount.data,
            payment_method=form.payment_method.data,
        )

        flash("Appointment booked.", "success")
        return redirect(url_for("appointments.detail", appointment_uuid=appointment.uuid))

    return render_template(
        "appointments/new.html",
        form=form,
        patient=patient,
        patients=patients,
        patient_query=patient_query,
    )


@appointments_bp.get("/<appointment_uuid>")
@login_required
@RBACService.require_permission("appointments.view")
def detail(appointment_uuid):
    appointment = Appointment.query.filter_by(uuid=appointment_uuid).first_or_404()

    return render_template(
        "appointments/detail.html",
        appointment=appointment,
        arrive_form=AppointmentArriveForm(),
        cancel_form=AppointmentCancelForm(),
        reschedule_form=AppointmentRescheduleForm(),
        AppointmentService=AppointmentService,
        PatientService=PatientService,
    )


@appointments_bp.route("/<appointment_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("appointments.manage")
def edit(appointment_uuid):
    appointment = Appointment.query.filter_by(uuid=appointment_uuid).first_or_404()
    form = AppointmentForm(obj=appointment)

    if request.method == "GET":
        form.patient_id.data = str(appointment.patient_id)

    if form.validate_on_submit():
        patient = _get_patient_from_form(form)

        if not patient:
            flash("Please select a patient.", "danger")
            return render_template("appointments/edit.html", form=form, appointment=appointment)

        AppointmentService.update_appointment(
            appointment,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
            duration_minutes=form.duration_minutes.data,
            appointment_type=form.appointment_type.data,
            source=form.source.data,
            notes=form.notes.data,
            fee_amount=form.fee_amount.data,
            paid_amount=form.paid_amount.data,
            payment_method=form.payment_method.data,
        )

        flash("Appointment updated.", "success")
        return redirect(url_for("appointments.detail", appointment_uuid=appointment.uuid))

    return render_template(
        "appointments/edit.html",
        form=form,
        appointment=appointment,
    )


@appointments_bp.post("/<appointment_uuid>/arrive")
@login_required
@RBACService.require_permission("appointments.manage")
def arrive(appointment_uuid):
    appointment = Appointment.query.filter_by(
        uuid=appointment_uuid,
    ).first_or_404()

    AppointmentService.mark_arrived(appointment)

    target = url_for(
        "today_clinic.day",
        clinic_date=(
            appointment.appointment_date.isoformat()
        ),
        resolved_filter=request.args.get(
            "resolved_filter",
            "all",
        ),
        resolved_sort=request.args.get(
            "resolved_sort",
            "latest",
        ),
    )

    if request.headers.get("HX-Request") == "true":
        return redirect(
            url_for(
                "today_clinic.dynamic",
                clinic_date=(
                    appointment
                    .appointment_date
                    .isoformat()
                ),
                resolved_filter=request.args.get(
                    "resolved_filter",
                    "all",
                ),
                resolved_sort=request.args.get(
                    "resolved_sort",
                    "latest",
                ),
            )
        )

    flash(
        "Patient marked as arrived / waiting.",
        "success",
    )
    return redirect(target)


@appointments_bp.post("/<appointment_uuid>/undo-arrive")
@login_required
@RBACService.require_permission("appointments.manage")
def undo_arrive(appointment_uuid):
    appointment = Appointment.query.filter_by(
        uuid=appointment_uuid,
    ).first_or_404()

    try:
        AppointmentService.undo_arrived(
            appointment
        )
    except ValueError as exc:
        flash(str(exc), "danger")
    else:
        flash(
            "Arrival was undone. Appointment returned "
            "to booked.",
            "info",
        )

    endpoint = (
        "today_clinic.dynamic"
        if request.headers.get("HX-Request") == "true"
        else "today_clinic.day"
    )

    return redirect(
        url_for(
            endpoint,
            clinic_date=(
                appointment.appointment_date.isoformat()
            ),
            resolved_filter=request.args.get(
                "resolved_filter",
                "all",
            ),
            resolved_sort=request.args.get(
                "resolved_sort",
                "latest",
            ),
        )
    )


@appointments_bp.post("/<appointment_uuid>/cancel")
@login_required
@RBACService.require_permission("appointments.manage")
def cancel(appointment_uuid):
    appointment = Appointment.query.filter_by(uuid=appointment_uuid).first_or_404()
    form = AppointmentCancelForm()

    if not form.validate_on_submit():
        flash("Cancel request was invalid.", "danger")
        return redirect(url_for("appointments.detail", appointment_uuid=appointment.uuid))

    AppointmentService.cancel_appointment(appointment, reason=form.reason.data)
    flash("Appointment cancelled.", "warning")
    return redirect(url_for("appointments.detail", appointment_uuid=appointment.uuid))


@appointments_bp.post("/<appointment_uuid>/reschedule")
@login_required
@RBACService.require_permission("appointments.manage")
def reschedule(appointment_uuid):
    appointment = Appointment.query.filter_by(uuid=appointment_uuid).first_or_404()
    form = AppointmentRescheduleForm()

    if not form.validate_on_submit():
        flash("Reschedule request was invalid.", "danger")
        return redirect(url_for("appointments.detail", appointment_uuid=appointment.uuid))

    new_appointment = AppointmentService.reschedule_appointment(
        appointment,
        new_date=form.appointment_date.data,
        new_time=form.appointment_time.data,
        updated_by_user_id=current_user.id,
    )

    flash("Appointment rescheduled.", "success")
    return redirect(url_for("appointments.detail", appointment_uuid=new_appointment.uuid))


@appointments_bp.route("/emergency/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("appointments.manage")
def emergency_new():
    patient_query = request.args.get("q", "")
    patients = PatientService.search_patients(patient_query, limit=10) if patient_query else []
    form = AppointmentForm()

    if request.method == "GET":
        form.appointment_type.data = Appointment.TYPE_EMERGENCY
        form.source.data = Appointment.SOURCE_EMERGENCY_UNSCHEDULED
        form.appointment_date.data = date.today()

    if form.validate_on_submit():
        patient = _get_patient_from_form(form)

        if not patient:
            flash("Please select a patient.", "danger")
            return render_template(
                "appointments/emergency_new.html",
                form=form,
                patients=patients,
                patient_query=patient_query,
            )

        appointment = AppointmentService.create_emergency_unscheduled(
            patient_id=patient.id,
            notes=form.notes.data,
            created_by_user_id=current_user.id,
        )

        flash("Emergency patient added to waiting queue.", "success")
        return redirect(url_for("appointments.detail", appointment_uuid=appointment.uuid))

    return render_template(
        "appointments/emergency_new.html",
        form=form,
        patients=patients,
        patient_query=patient_query,
    )
