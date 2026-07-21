from calendar import Calendar, month_name
from datetime import date, datetime, timedelta
import json

from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.appointment_forms import (
    AppointmentArriveForm,
    AppointmentCancelForm,
    AppointmentEmergencyForm,
    AppointmentForm,
    AppointmentQuickEditForm,
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

    try:
        return db.session.get(Patient, int(patient_id))
    except (TypeError, ValueError):
        return None


def _create_patient_from_appointment_form(form):
    return PatientService.create_patient(
        commit=False,
        name_ar=form.new_patient_name_ar.data,
        name_en=form.new_patient_name_en.data,
        phone_primary=form.new_patient_phone_primary.data,
        phone_secondary=form.new_patient_phone_secondary.data,
        email=form.new_patient_email.data,
        date_of_birth=form.new_patient_date_of_birth.data,
        age_years_at_registration=(
            form.new_patient_age_years_at_registration.data
        ),
        marital_status=form.new_patient_marital_status.data,
        is_virgin=form.new_patient_is_virgin.data,
        occupation=form.new_patient_occupation.data,
        governorate=form.new_patient_governorate.data,
        city=form.new_patient_city.data,
        street=form.new_patient_street.data,
    )


def _resolve_appointment_patient(form):
    if form.patient_mode.data == "new":
        if not RBACService.user_has_permission(
            current_user,
            "patients.basic.create",
        ):
            raise ValueError("You do not have permission to create patients.")
        return _create_patient_from_appointment_form(form), True

    patient = _get_patient_from_form(form)
    if patient is None:
        raise ValueError("Please select a valid patient.")
    return patient, False


def _booking_form_context(**context):
    context.update(
        PatientService=PatientService,
        can_create_patient=RBACService.user_has_permission(
            current_user,
            "patients.basic.create",
        ),
    )
    return context


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
    form = AppointmentForm()

    if patient and request.method == "GET":
        form.patient_id.data = str(patient.id)
        form.patient_mode.data = "existing"

    if form.validate_on_submit():
        try:
            patient, patient_was_created = _resolve_appointment_patient(form)
            appointment = AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=form.appointment_date.data,
                appointment_time=form.appointment_time.data,
                appointment_type=form.appointment_type.data,
                source=form.source.data,
                notes=form.notes.data,
                fee_amount=form.fee_amount.data,
                paid_amount=form.paid_amount.data,
                payment_method=form.payment_method.data,
                created_by_user_id=current_user.id,
            )
        except ValueError as exc:
            form.patient_id.errors.append(str(exc))
        else:
            if patient_was_created and PatientService.find_duplicate_phone_patients(
                patient.phone_primary,
                exclude_patient_id=patient.id,
            ):
                flash(
                    "Appointment booked. Warning: another patient uses this phone number.",
                    "warning",
                )
            else:
                flash("Appointment booked.", "success")
            return redirect(url_for("appointments.detail", appointment_uuid=appointment.uuid))

    return render_template("appointments/new.html", **_booking_form_context(
        form=form,
        patient=patient,
        patient_query="",
    ))


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
        form.patient_mode.data = "existing"

    if form.validate_on_submit():
        patient = _get_patient_from_form(form)

        if not patient:
            flash("Please select a patient.", "danger")
            return render_template(
                "appointments/edit.html",
                form=form,
                appointment=appointment,
                PatientService=PatientService,
                can_create_patient=False,
            )

        AppointmentService.update_appointment(
            appointment,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
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
        PatientService=PatientService,
        can_create_patient=False,
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


@appointments_bp.get(
    "/<appointment_uuid>/cancel/modal"
)
@login_required
@RBACService.require_permission("appointments.manage")
def cancel_modal(appointment_uuid):
    appointment = Appointment.query.filter_by(
        uuid=appointment_uuid,
    ).first_or_404()

    form = AppointmentCancelForm()

    return render_template(
        "clinic/actions/_cancel_form.html",
        appointment=appointment,
        form=form,
        resolved_filter=request.args.get(
            "resolved_filter",
            "all",
        ),
        resolved_sort=request.args.get(
            "resolved_sort",
            "latest",
        ),
        PatientService=PatientService,
    )


@appointments_bp.get(
    "/<appointment_uuid>/reschedule/modal"
)
@login_required
@RBACService.require_permission("appointments.manage")
def reschedule_modal(appointment_uuid):
    appointment = Appointment.query.filter_by(
        uuid=appointment_uuid,
    ).first_or_404()

    form = AppointmentRescheduleForm()

    return render_template(
        "clinic/actions/_reschedule_form.html",
        appointment=appointment,
        form=form,
        action_error=None,
        resolved_filter=request.args.get(
            "resolved_filter",
            "all",
        ),
        resolved_sort=request.args.get(
            "resolved_sort",
            "latest",
        ),
        PatientService=PatientService,
    )


@appointments_bp.post("/<appointment_uuid>/cancel")
@login_required
@RBACService.require_permission("appointments.manage")
def cancel(appointment_uuid):
    appointment = Appointment.query.filter_by(
        uuid=appointment_uuid,
    ).first_or_404()

    form = AppointmentCancelForm()
    is_htmx = (
        request.headers.get("HX-Request") == "true"
    )
    resolved_filter = request.args.get(
        "resolved_filter",
        "all",
    )
    resolved_sort = request.args.get(
        "resolved_sort",
        "latest",
    )

    if not form.validate_on_submit():
        if is_htmx:
            return render_template(
                "clinic/actions/_cancel_form.html",
                appointment=appointment,
                form=form,
                resolved_filter=resolved_filter,
                resolved_sort=resolved_sort,
                PatientService=PatientService,
            )

        flash(
            "Cancel request was invalid.",
            "danger",
        )

        return redirect(
            url_for(
                "appointments.detail",
                appointment_uuid=appointment.uuid,
            )
        )

    try:
        AppointmentService.cancel_appointment(
            appointment,
            reason=form.reason.data,
        )
    except ValueError as exc:
        if is_htmx:
            form.reason.errors = tuple(
                list(form.reason.errors)
                + [str(exc)]
            )

            return render_template(
                "clinic/actions/_cancel_form.html",
                appointment=appointment,
                form=form,
                resolved_filter=resolved_filter,
                resolved_sort=resolved_sort,
                PatientService=PatientService,
            )

        flash(str(exc), "danger")

        return redirect(
            url_for(
                "appointments.detail",
                appointment_uuid=appointment.uuid,
            )
        )

    if is_htmx:
        response = make_response("", 204)

        response.headers["HX-Trigger"] = json.dumps(
            {
                "clinic:action-success": {
                    "message": (
                        "Appointment cancelled."
                    ),
                    "tone": "warning",
                }
            }
        )

        return response

    flash(
        "Appointment cancelled.",
        "warning",
    )

    return redirect(
        url_for(
            "today_clinic.day",
            clinic_date=(
                appointment.appointment_date.isoformat()
            ),
            resolved_filter=resolved_filter,
            resolved_sort=resolved_sort,
        )
    )


@appointments_bp.post("/<appointment_uuid>/reschedule")
@login_required
@RBACService.require_permission("appointments.manage")
def reschedule(appointment_uuid):
    appointment = Appointment.query.filter_by(
        uuid=appointment_uuid,
    ).first_or_404()

    form = AppointmentRescheduleForm()
    is_htmx = (
        request.headers.get("HX-Request") == "true"
    )
    resolved_filter = request.args.get(
        "resolved_filter",
        "all",
    )
    resolved_sort = request.args.get(
        "resolved_sort",
        "latest",
    )

    if not form.validate_on_submit():
        if is_htmx:
            return render_template(
                "clinic/actions/_reschedule_form.html",
                appointment=appointment,
                form=form,
                action_error=None,
                resolved_filter=resolved_filter,
                resolved_sort=resolved_sort,
                PatientService=PatientService,
            )

        flash(
            "Reschedule request was invalid.",
            "danger",
        )

        return redirect(
            url_for(
                "appointments.detail",
                appointment_uuid=appointment.uuid,
            )
        )

    try:
        AppointmentService.reschedule_appointment(
            appointment,
            new_date=form.appointment_date.data,
            new_time=form.appointment_time.data,
            updated_by_user_id=current_user.id,
        )
    except ValueError as exc:
        if is_htmx:
            return render_template(
                "clinic/actions/_reschedule_form.html",
                appointment=appointment,
                form=form,
                action_error=str(exc),
                resolved_filter=resolved_filter,
                resolved_sort=resolved_sort,
                PatientService=PatientService,
            )

        flash(str(exc), "danger")

        return redirect(
            url_for(
                "appointments.detail",
                appointment_uuid=appointment.uuid,
            )
        )

    if is_htmx:
        response = make_response("", 204)

        response.headers["HX-Trigger"] = json.dumps(
            {
                "clinic:action-success": {
                    "message": (
                        "Appointment rescheduled."
                    ),
                    "tone": "success",
                }
            }
        )

        return response

    flash(
        "Appointment rescheduled.",
        "success",
    )

    return redirect(
        url_for(
            "today_clinic.day",
            clinic_date=(
                appointment.appointment_date.isoformat()
            ),
            resolved_filter=resolved_filter,
            resolved_sort=resolved_sort,
        )
    )



@appointments_bp.get("/patient-options")
@login_required
@RBACService.require_permission("appointments.manage")
def patient_options():
    patient_query = request.args.get("q", "").strip()
    patients = (
        PatientService.search_patients(patient_query, limit=8)
        if patient_query
        else []
    )
    selector_id = request.args.get("selector_id", "booking-patient")
    selector_id = "".join(
        character
        for character in selector_id
        if character.isalnum() or character in {"-", "_"}
    ) or "booking-patient"

    return render_template(
        "appointments/_patient_options.html",
        patients=patients,
        patient_query=patient_query,
        selector_id=selector_id,
        PatientService=PatientService,
        can_create_patient=RBACService.user_has_permission(
            current_user,
            "patients.basic.create",
        ),
    )


@appointments_bp.get("/emergency/modal")
@login_required
@RBACService.require_permission("appointments.manage")
def emergency_modal():
    form = AppointmentEmergencyForm()

    return render_template("clinic/actions/_emergency_form.html", **_booking_form_context(
        form=form,
        patient_query="",
    ))


@appointments_bp.post("/emergency")
@login_required
@RBACService.require_permission("appointments.manage")
def emergency_create():
    form = AppointmentEmergencyForm()
    is_htmx = request.headers.get("HX-Request") == "true"

    if not form.validate_on_submit():
        if is_htmx:
            return render_template("clinic/actions/_emergency_form.html", **_booking_form_context(
                form=form,
                patient_query="",
            ))

        flash("Emergency request was invalid.", "danger")
        return redirect(url_for("appointments.emergency_new"))

    try:
        patient, patient_was_created = _resolve_appointment_patient(form)
        AppointmentService.create_emergency_unscheduled(
            patient_id=patient.id,
            appointment_time=datetime.now().time().replace(
                second=0,
                microsecond=0,
            ),
            fee_amount=form.fee_amount.data,
            paid_amount=form.paid_amount.data,
            payment_method=form.payment_method.data,
            notes=form.notes.data,
            created_by_user_id=current_user.id,
        )
    except ValueError as exc:
        form.patient_id.errors.append(str(exc))

        if is_htmx:
            return render_template("clinic/actions/_emergency_form.html", **_booking_form_context(
                form=form,
                patient_query="",
            ))

        flash(str(exc), "danger")
        return redirect(url_for("appointments.emergency_new"))

    if is_htmx:
        response = make_response("", 204)
        message = "Emergency patient added to Waiting."
        if patient_was_created:
            message = "New patient created and added to Waiting as an emergency."
            if PatientService.find_duplicate_phone_patients(
                patient.phone_primary,
                exclude_patient_id=patient.id,
            ):
                message += " Warning: another patient uses this phone number."
        response.headers["HX-Trigger"] = json.dumps(
            {
                "clinic:action-success": {
                    "message": message,
                    "tone": "warning",
                }
            }
        )
        return response

    flash(
        "Emergency patient added to waiting queue.",
        "success",
    )
    return redirect(
        url_for(
            "today_clinic.day",
            clinic_date=date.today().isoformat(),
        )
    )


@appointments_bp.get("/<appointment_uuid>/quick-edit/modal")
@login_required
@RBACService.require_permission("appointments.manage")
def quick_edit_modal(appointment_uuid):
    appointment = Appointment.query.filter_by(
        uuid=appointment_uuid,
    ).first_or_404()

    if (
        appointment.status not in AppointmentService.ACTIVE_STATUSES
        or appointment.visit is not None
    ):
        return ("Quick Edit is unavailable for this appointment.", 409)

    form = AppointmentQuickEditForm(obj=appointment)

    return render_template(
        "clinic/actions/_quick_edit_form.html",
        appointment=appointment,
        form=form,
        resolved_filter=request.args.get(
            "resolved_filter",
            "all",
        ),
        resolved_sort=request.args.get(
            "resolved_sort",
            "latest",
        ),
        PatientService=PatientService,
    )


@appointments_bp.post("/<appointment_uuid>/quick-edit")
@login_required
@RBACService.require_permission("appointments.manage")
def quick_edit(appointment_uuid):
    appointment = Appointment.query.filter_by(
        uuid=appointment_uuid,
    ).first_or_404()
    form = AppointmentQuickEditForm()
    is_htmx = request.headers.get("HX-Request") == "true"
    resolved_filter = request.args.get("resolved_filter", "all")
    resolved_sort = request.args.get("resolved_sort", "latest")

    action_error = None

    if (
        appointment.status not in AppointmentService.ACTIVE_STATUSES
        or appointment.visit is not None
    ):
        action_error = (
            "Quick Edit is unavailable after a Visit starts "
            "or after the appointment is resolved."
        )

    if action_error is None and form.validate_on_submit():
        try:
            AppointmentService.update_appointment(
                appointment,
                appointment_time=form.appointment_time.data,
                appointment_type=form.appointment_type.data,
                notes=form.notes.data,
                fee_amount=form.fee_amount.data,
                paid_amount=form.paid_amount.data,
                payment_method=form.payment_method.data,
                updated_by_user_id=current_user.id,
            )
        except ValueError as exc:
            action_error = str(exc)
    elif action_error is None:
        action_error = None

    if action_error is not None or not form.validate():
        if action_error:
            form.notes.errors = tuple(
                list(form.notes.errors) + [action_error]
            )

        if is_htmx:
            return render_template(
                "clinic/actions/_quick_edit_form.html",
                appointment=appointment,
                form=form,
                resolved_filter=resolved_filter,
                resolved_sort=resolved_sort,
                PatientService=PatientService,
            )

        flash(
            action_error or "Quick Edit request was invalid.",
            "danger",
        )
        return redirect(
            url_for(
                "appointments.edit",
                appointment_uuid=appointment.uuid,
            )
        )

    if is_htmx:
        response = make_response("", 204)
        response.headers["HX-Trigger"] = json.dumps(
            {
                "clinic:action-success": {
                    "message": "Appointment updated.",
                    "tone": "success",
                }
            }
        )
        return response

    flash("Appointment updated.", "success")
    return redirect(
        url_for(
            "today_clinic.day",
            clinic_date=appointment.appointment_date.isoformat(),
            resolved_filter=resolved_filter,
            resolved_sort=resolved_sort,
        )
    )


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
            appointment_time=datetime.now().time().replace(
                second=0,
                microsecond=0,
            ),
            fee_amount=form.fee_amount.data,
            paid_amount=form.paid_amount.data,
            payment_method=form.payment_method.data,
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
