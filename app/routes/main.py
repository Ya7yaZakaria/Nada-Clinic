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
        "investigations": RBACService.user_has_permission(current_user, "investigations.view"),
        "ultrasound": RBACService.user_has_permission(current_user, "ultrasound.view"),
        "surgeries": RBACService.user_has_permission(current_user, "surgeries.view"),
        "prescriptions": RBACService.user_has_permission(current_user, "prescriptions.view"),
        "documents": RBACService.user_has_permission(current_user, "documents.view"),
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

    visit_summary = DashboardService.get_visit_summary(date_from, date_to) if permissions["clinical"] else None
    upcoming_appointments = DashboardService.get_upcoming_appointments() if permissions["appointments"] else None
    investigation_summary = DashboardService.get_investigation_summary(date_from, date_to) if permissions["investigations"] else None
    ultrasound_summary = DashboardService.get_ultrasound_summary(date_from, date_to) if permissions["ultrasound"] else None
    surgery_summary = DashboardService.get_surgery_summary(date_from, date_to) if permissions["surgeries"] else None
    upcoming_surgeries = DashboardService.get_upcoming_surgeries() if permissions["surgeries"] else None
    module_activity = DashboardService.get_module_activity(
        date_from, date_to,
        include_prescriptions=permissions["prescriptions"],
        include_documents=permissions["documents"],
    ) if permissions["prescriptions"] or permissions["documents"] else {}
    revenue_by_service = DashboardService.get_revenue_by_service(date_from, date_to) if permissions["finance_insights"] else None

    needs_attention = (
        DashboardService.build_needs_attention(
            appointment_summary=(
                appointment_summary
                if permissions["appointments"]
                else None
            ),
            investigation_summary=(
                investigation_summary
            ),
            ultrasound_summary=(
                ultrasound_summary
            ),
            surgery_summary=surgery_summary,
            finance_summary=finance_summary,
        )
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

    if visit_summary:
        chart_data["visit_types"] = {
            "labels": visit_summary["labels"],
            "values": visit_summary["values"],
        }

    if revenue_by_service:
        chart_data[
            "revenue_services"
        ] = revenue_by_service

    if appointment_summary:
        chart_data[
            "appointment_types"
        ] = appointment_summary["types"]
        chart_data[
            "appointment_sources"
        ] = appointment_summary["sources"]

    if ultrasound_summary:
        chart_data["ultrasound_types"] = {
            "labels": ultrasound_summary[
                "labels"
            ],
            "values": ultrasound_summary[
                "values"
            ],
        }

    if surgery_summary:
        chart_data["surgery_statuses"] = {
            "labels": surgery_summary["labels"],
            "values": surgery_summary["values"],
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
        visit_summary=visit_summary,
        upcoming_appointments=upcoming_appointments,
        investigation_summary=investigation_summary,
        ultrasound_summary=ultrasound_summary,
        surgery_summary=surgery_summary,
        upcoming_surgeries=upcoming_surgeries,
        module_activity=module_activity,
        revenue_by_service=revenue_by_service,
        needs_attention=needs_attention,
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
