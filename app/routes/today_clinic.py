from datetime import date, datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.appointment_service import AppointmentService
from app.services.clinic_day_service import ClinicDayService
from app.services.finance_service import FinanceService
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
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


@today_clinic_bp.get("/previous")
@login_required
@RBACService.require_permission("appointments.view")
def previous():
    previous_days = AppointmentService.get_previous_clinic_days()

    return render_template(
        "clinic/previous.html",
        previous_days=previous_days,
        AppointmentService=AppointmentService,
    )


@today_clinic_bp.get("/day/<clinic_date>")
@login_required
@RBACService.require_permission("appointments.view")
def day(clinic_date):
    selected_date = _parse_clinic_date(clinic_date)
    resolved = AppointmentService.get_resolved_bookings(
        selected_date,
        request.args.get("resolved_filter", "all"),
        request.args.get("resolved_sort", "latest"),
    )

    if selected_date < date.today():
        clinic_day = AppointmentService.get_day_summary(
            selected_date
        )
        visit_snapshot = (
            ClinicDayService.get_visit_snapshot(
                selected_date
            )
        )

        return render_template(
            "clinic/past_day.html",
            clinic_day=clinic_day,
            selected_date=selected_date,
            visit_snapshot=visit_snapshot,
            resolved=resolved,
            AppointmentService=AppointmentService,
            JourneyService=JourneyService,
            PatientService=PatientService,
            VisitService=VisitService,
        )

    clinic_day = AppointmentService.get_clinic_day(
        selected_date
    )
    visit_snapshot = (
        ClinicDayService.get_visit_snapshot(
            selected_date
        )
    )
    live_counters = (
        ClinicDayService.build_live_counters(
            clinic_day,
            visit_snapshot,
        )
    )
    clinic_intelligence = (
        ClinicDayService.build_intelligence(
            clinic_day,
            visit_snapshot,
            now=datetime.now(timezone.utc),
        )
    )

    display_timezone = SettingsService.get(
        "localization.timezone",
        default="Africa/Cairo",
    )

    finance_summary = None
    if RBACService.user_has_permission(
        current_user,
        "finance.insights",
    ):
        finance_summary = (
            FinanceService.get_insights_summary(
                selected_date,
                selected_date,
            )
        )

    return render_template(
        "clinic/today.html",
        clinic_day=clinic_day,
        selected_date=selected_date,
        visit_snapshot=visit_snapshot,
        resolved=resolved,
        live_counters=live_counters,
        clinic_intelligence=clinic_intelligence,
        display_timezone=display_timezone,
        finance_summary=finance_summary,
        show_close_result=(
            ClinicDayService
            .is_close_result_visible(clinic_day)
        ),
        AppointmentService=AppointmentService,
        JourneyService=JourneyService,
        PatientService=PatientService,
        VisitService=VisitService,
    )


@today_clinic_bp.post("/day/<clinic_date>/close")
@login_required
@RBACService.require_permission("appointments.manage")
def close_day(clinic_date):
    selected_date = _parse_clinic_date(
        clinic_date
    )

    converted = AppointmentService.close_clinic_day(
        selected_date
    )

    flash(
        "Clinic day closed. "
        f"{len(converted)} remaining booking(s) "
        "converted to no-show.",
        "warning",
    )

    return redirect(
        url_for(
            "today_clinic.day",
            clinic_date=selected_date.isoformat(),
        )
    )
