from flask import (
    Blueprint,
    flash,
    jsonify,
    render_template,
    request,
)
from flask_login import (
    current_user,
    login_required,
)

from app.services.dashboard_service import (
    DashboardService,
)
from app.services.rbac_service import (
    RBACService,
)

main_bp = Blueprint(
    "main",
    __name__,
)


@main_bp.get("/")
@login_required
@RBACService.require_permission(
    "dashboard.view"
)
def index():
    period = DashboardService.resolve_period(
        request.args.get("date_from"),
        request.args.get("date_to"),
        request.args.get("preset"),
    )

    if period["was_invalid"]:
        flash(
            "Invalid date range. "
            "Showing this month instead.",
            "warning",
        )

    permissions = {
        "patients": (
            RBACService.user_has_permission(
                current_user,
                "patients.basic.view",
            )
        ),
        "appointments": (
            RBACService.user_has_permission(
                current_user,
                "appointments.view",
            )
        ),
        "clinical": (
            RBACService.user_has_permission(
                current_user,
                "clinical.view",
            )
        ),
        "finance_insights": (
            RBACService.user_has_permission(
                current_user,
                "finance.insights",
            )
        ),
    }

    date_from = period["date_from"]
    date_to = period["date_to"]

    clinic_kpis = (
        DashboardService.get_clinic_kpis(
            date_from,
            date_to,
            include_patients=(
                permissions["patients"]
            ),
            include_visits=(
                permissions["clinical"]
            ),
            include_appointments=(
                permissions["appointments"]
            ),
        )
    )

    has_activity_permission = any(
        (
            permissions["patients"],
            permissions["clinical"],
            permissions["appointments"],
        )
    )

    activity_trend = (
        DashboardService.get_activity_trend(
            date_from,
            date_to,
            include_patients=(
                permissions["patients"]
            ),
            include_visits=(
                permissions["clinical"]
            ),
            include_appointments=(
                permissions["appointments"]
            ),
        )
        if has_activity_permission
        else None
    )

    journey_mix = (
        DashboardService.get_journey_mix(
            date_from,
            date_to,
        )
        if permissions["clinical"]
        else None
    )

    appointment_summary = (
        DashboardService
        .get_appointment_summary(
            date_from,
            date_to,
        )
        if permissions["appointments"]
        else None
    )

    finance_summary = (
        DashboardService
        .get_finance_summary(
            date_from,
            date_to,
        )
        if permissions["finance_insights"]
        else None
    )

    today_clinic = (
        DashboardService
        .get_today_clinic_snapshot()
        if permissions["appointments"]
        else None
    )

    chart_data = {
        "activity": activity_trend,
        "journeys": journey_mix,
        "appointments": (
            {
                "labels": (
                    appointment_summary[
                        "labels"
                    ]
                ),
                "values": (
                    appointment_summary[
                        "values"
                    ]
                ),
            }
            if appointment_summary
            else None
        ),
        "finance": (
            finance_summary["daily"]
            if finance_summary
            else None
        ),
    }

    return render_template(
        "index.html",
        period=period,
        permissions=permissions,
        clinic_kpis=clinic_kpis,
        journey_mix=journey_mix,
        appointment_summary=(
            appointment_summary
        ),
        finance_summary=finance_summary,
        today_clinic=today_clinic,
        dashboard_chart_data=chart_data,
    )


@main_bp.get(
    "/clinical-placeholder"
)
@login_required
@RBACService.require_permission(
    "clinical.note.view"
)
def clinical_placeholder():
    return render_template(
        "placeholders/clinical.html",
        title="Clinical Placeholder",
    )


@main_bp.get(
    "/reception-placeholder"
)
@login_required
@RBACService.require_permission(
    "appointments.manage"
)
def reception_placeholder():
    return render_template(
        "placeholders/reception.html",
        title="Reception Placeholder",
    )


@main_bp.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": (
                "Nada Clinic System"
            ),
            "migration_baseline": (
                "20260715_0069"
            ),
        }
    ), 200
