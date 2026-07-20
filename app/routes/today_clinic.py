from datetime import date, datetime, timezone

from flask import (
    Blueprint,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
import json
from flask_login import current_user, login_required

from app.extensions import db
from app.services.appointment_service import AppointmentService
from app.services.clinic_day_service import ClinicDayService
from app.services.clinic_day_state_service import (
    ClinicDayStateService,
)
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


def _require_current_close_day_date(value):
    try:
        selected_date = date.fromisoformat(value)
    except (TypeError, ValueError):
        abort(404)

    if selected_date != date.today():
        abort(
            409,
            description=(
                "Close Day is available only for "
                "the current clinic date."
            ),
        )

    return selected_date

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


def _build_live_context(
    selected_date,
    resolved_filter="all",
    resolved_sort="latest",
):
    clinic_day = AppointmentService.get_clinic_day(
        selected_date
    )
    visit_snapshot = (
        ClinicDayService.get_visit_snapshot(
            selected_date
        )
    )
    resolved = AppointmentService.get_resolved_bookings(
        selected_date,
        resolved_filter,
        resolved_sort,
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

    return {
        "clinic_day": clinic_day,
        "selected_date": selected_date,
        "visit_snapshot": visit_snapshot,
        "resolved": resolved,
        "live_counters": live_counters,
        "clinic_intelligence": clinic_intelligence,
        "finance_summary": finance_summary,
        "day_state": ClinicDayStateService.get_state(
            selected_date
        ),
        "is_day_closed": (
            ClinicDayStateService.is_closed(
                selected_date
            )
        ),
        "closing_summary": (
            ClinicDayService.build_closing_summary(
                clinic_day,
                visit_snapshot,
            )
        ),
        "enable_live_actions": True,
        "AppointmentService": AppointmentService,
        "ClinicDayService": ClinicDayService,
        "JourneyService": JourneyService,
        "PatientService": PatientService,
        "VisitService": VisitService,
    }


@today_clinic_bp.get("/day/<clinic_date>")
@login_required
@RBACService.require_permission("appointments.view")
def day(clinic_date):
    selected_date = _parse_clinic_date(clinic_date)
    resolved_filter = request.args.get(
        "resolved_filter",
        "all",
    )
    resolved_sort = request.args.get(
        "resolved_sort",
        "latest",
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
        resolved = (
            AppointmentService.get_resolved_bookings(
                selected_date,
                resolved_filter,
                resolved_sort,
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

    context = _build_live_context(
        selected_date,
        resolved_filter,
        resolved_sort,
    )
    context.update(
        display_timezone=SettingsService.get(
            "localization.timezone",
            default="Africa/Cairo",
        ),
        show_close_result=context["is_day_closed"],
    )

    return render_template(
        "clinic/today.html",
        **context,
    )


@today_clinic_bp.get("/day/<clinic_date>/dynamic")
@login_required
@RBACService.require_permission("appointments.view")
def dynamic(clinic_date):
    selected_date = _parse_clinic_date(clinic_date)

    if selected_date < date.today():
        return redirect(
            url_for(
                "today_clinic.day",
                clinic_date=selected_date.isoformat(),
            )
        )

    context = _build_live_context(
        selected_date,
        request.args.get("resolved_filter", "all"),
        request.args.get("resolved_sort", "latest"),
    )

    context["is_htmx_partial"] = True

    return render_template(
        "clinic/_today_dynamic.html",
        **context,
    )



@today_clinic_bp.get("/day/<clinic_date>/close/preview")
@login_required
@RBACService.require_permission("appointments.manage")
def close_day_preview(clinic_date):
    selected_date = _require_current_close_day_date(
        clinic_date
    )

    if ClinicDayStateService.is_closed(selected_date):
        abort(
            409,
            description="Clinic day is already closed.",
        )

    booked_count = len(
        AppointmentService.get_booked_no_action(selected_date)
    )
    waiting_count = len(
        AppointmentService.get_waiting_queue(selected_date)
    )
    visit_snapshot = ClinicDayService.get_visit_snapshot(
        selected_date
    )

    def snapshot_value(name):
        if isinstance(visit_snapshot, dict):
            return int(visit_snapshot.get(name, 0) or 0)
        return int(getattr(visit_snapshot, name, 0) or 0)

    unresolved_visits = (
        snapshot_value("open")
        + snapshot_value("incomplete")
    )

    return render_template(
        "clinic/actions/_close_day_preview.html",
        selected_date=selected_date,
        booked_count=booked_count,
        waiting_count=waiting_count,
        unresolved_visits=unresolved_visits,
    )


@today_clinic_bp.post("/day/<clinic_date>/close")
@login_required
@RBACService.require_permission("appointments.manage")
def close_day(clinic_date):
    selected_date = _require_current_close_day_date(
        clinic_date
    )

    if ClinicDayStateService.is_closed(selected_date):
        abort(
            409,
            description="Clinic day is already closed.",
        )

    try:
        AppointmentService.close_clinic_day(
            selected_date,
            commit=False,
        )

        ClinicDayStateService.close_day(
            selected_date,
            commit=False,
        )

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    if request.headers.get("HX-Request") == "true":
        response = make_response("", 204)

        response.headers["HX-Redirect"] = url_for(
            "today_clinic.day",
            clinic_date=selected_date.isoformat(),
        )

        return response

    flash(
        "Clinic day closed. Operational and financial "
        "editing is now locked.",
        "warning",
    )
    return redirect(
        url_for(
            "today_clinic.day",
            clinic_date=selected_date.isoformat(),
        )
    )

@today_clinic_bp.post("/day/<clinic_date>/reopen")
@login_required
@RBACService.require_permission("clinic_day.reopen")
def reopen_day(clinic_date):
    selected_date = _require_current_close_day_date(
        clinic_date
    )

    ClinicDayStateService.reopen_day(selected_date)

    if request.headers.get("HX-Request") == "true":
        response = make_response("", 204)

        response.headers["HX-Redirect"] = url_for(
            "today_clinic.day",
            clinic_date=selected_date.isoformat(),
        )

        return response

    flash("Clinic day reopened.", "success")

    return redirect(
        url_for(
            "today_clinic.day",
            clinic_date=selected_date.isoformat(),
        )
    )
