from datetime import date

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.visit_service import VisitService


today_clinic_bp = Blueprint("today_clinic", __name__, url_prefix="/clinic")


def _parse_clinic_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return date.today()


@today_clinic_bp.get("/today")
@login_required
@RBACService.require_permission("appointments.view")
def index():
    return redirect(url_for("today_clinic.day", clinic_date=date.today().isoformat()))


@today_clinic_bp.get("/day/<clinic_date>")
@login_required
@RBACService.require_permission("appointments.view")
def day(clinic_date):
    selected_date = _parse_clinic_date(clinic_date)
    clinic_day = AppointmentService.get_clinic_day(selected_date)

    return render_template(
        "clinic/today.html",
        clinic_day=clinic_day,
        selected_date=selected_date,
        AppointmentService=AppointmentService,
        JourneyService=JourneyService,
        PatientService=PatientService,
        VisitService=VisitService,
    )


@today_clinic_bp.post("/day/<clinic_date>/close")
@login_required
@RBACService.require_permission("appointments.manage")
def close_day(clinic_date):
    selected_date = _parse_clinic_date(clinic_date)
    converted = AppointmentService.close_clinic_day(selected_date)

    flash(f"Clinic day closed. {len(converted)} booked appointment(s) converted to no-show.", "warning")
    return redirect(url_for("today_clinic.day", clinic_date=selected_date.isoformat()))


@today_clinic_bp.post("/appointments/<appointment_uuid>/complete")
@login_required
@RBACService.require_permission("appointments.manage")
def complete_appointment(appointment_uuid):
    appointment = Appointment.query.filter_by(uuid=appointment_uuid).first_or_404()

    AppointmentService.mark_completed(appointment)
    flash("Appointment marked completed.", "success")
    return redirect(url_for("today_clinic.day", clinic_date=appointment.appointment_date.isoformat()))
