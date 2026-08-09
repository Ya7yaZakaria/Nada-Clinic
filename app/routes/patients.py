from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.appointment_forms import AppointmentForm

from app.forms.patient_forms import MRNChangeForm, PatientForm
from app.models import Journey, Patient
from app.services.appointment_service import AppointmentService
from app.services.clinic_ultrasound_service import ClinicUltrasoundService
from app.services.external_ultrasound_service import ExternalUltrasoundService
from app.services.finance_service import FinanceService
from app.services.document_service import DocumentService
from app.services.investigation_preset_service import InvestigationPresetService
from app.services.investigation_service import InvestigationService
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.patient_dashboard_service import PatientDashboardService
from app.services.partner_service import PartnerService
from app.services.partner_semen_analysis_service import PartnerSemenAnalysisService
from app.services.rbac_service import RBACService
from app.services.surgery_service import SurgeryService
from app.services.timeline_service import TimelineService
from app.services.visit_service import VisitService

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


def _patient_directory_context():
    can_view_clinical = RBACService.user_has_permission(current_user, "clinical.view")
    can_view_finance = RBACService.user_has_permission(current_user, "finance.view")
    can_manage_appointments = RBACService.user_has_permission(
        current_user,
        "appointments.manage",
    )
    can_start_visit = RBACService.user_has_permission(
        current_user,
        "clinical.note.write",
    )

    filters = {
        "q": (request.args.get("q") or "").strip(),
        "status": request.args.get("status", "active"),
        "journey": request.args.get("journey", "all"),
        "last_seen": request.args.get("last_seen", "any"),
        "upcoming": request.args.get("upcoming") == "1",
        "pending_results": request.args.get("pending_results") == "1",
        "outstanding": request.args.get("outstanding") == "1",
        "sort": request.args.get("sort", "recently_seen"),
    }

    directory = PatientDashboardService.list_patients(
        **filters,
        page=request.args.get("page", 1, type=int),
        can_view_clinical=can_view_clinical,
        can_view_finance=can_view_finance,
    )

    return {
        "directory": directory,
        "filters": filters,
        "PatientService": PatientService,
        "can_view_clinical": can_view_clinical,
        "can_view_finance": can_view_finance,
        "can_manage_appointments": can_manage_appointments,
        "can_start_visit": can_start_visit,
    }


def _patient_quick_list_context(cohort):
    can_view_clinical = RBACService.user_has_permission(current_user, "clinical.view")
    can_view_finance = RBACService.user_has_permission(current_user, "finance.view")
    can_manage_appointments = RBACService.user_has_permission(
        current_user,
        "appointments.manage",
    )
    can_start_visit = RBACService.user_has_permission(current_user, "clinical.note.write")

    valid_cohorts = {
        "active": ("Active patients", "Current active patient records"),
        "new_this_month": ("New this month", "Patients registered during the current month"),
        "seen_30_days": ("Seen in 30 days", "Patients with a visit in the last 30 days"),
        "attention": ("Need attention", "Patients with an item that needs follow-up"),
        "new_period": ("New patients", "Registered during the selected analytics period"),
        "returning": ("Returning patients", "Established patients seen during the selected period"),
        "seen_recent": ("Recently seen", "Patients seen within the last six months"),
        "dormant": ("Dormant patients", "Active patients not seen within the last six months"),
        "never_seen": ("Never seen", "Registered patients without a visit"),
        "follow_up_overdue": ("Overdue follow-ups", "Patients with a recorded follow-up date in the past"),
        "follow_up_upcoming": ("Upcoming follow-ups", "Patients with a future follow-up date"),
        "pending_review": ("Pending reviews", "Patients with investigation results awaiting review"),
        "outstanding": ("Outstanding balances", "Patients with an unpaid or partial balance"),
        "appointment": ("Appointment activity", "Patients in the selected appointment group"),
        "age": ("Age group", "Patients in the selected recorded age range"),
    }
    q = (request.args.get("q") or "").strip()
    sort = request.args.get("sort", "urgent" if cohort == "attention" else "recently_seen")
    if sort not in PatientDashboardService.VALID_DRAWER_SORTS:
        sort = "recently_seen"
    period = request.args.get("period", "6m")
    segment = request.args.get("segment")
    journey = request.args.get("journey")
    if journey in {"pregnancy", "infertility", "gynecology"} and can_view_clinical:
        title = f"{journey.replace('gynecology', 'Gynecology').title()} journeys"
        subtitle = "Patients currently active in this care journey"
        directory = PatientDashboardService.list_patients(
            q=q,
            status="active",
            journey=journey,
            sort=sort,
            per_page=30,
            can_view_clinical=True,
            can_view_finance=can_view_finance,
        )
    else:
        cohort = cohort if cohort in valid_cohorts else "active"
        title, subtitle = valid_cohorts[cohort]
        directory = PatientDashboardService.list_patients(
            q=q,
            status="active",
            cohort=cohort,
            segment=segment,
            period=period,
            sort="newest" if cohort == "new_this_month" and not request.args.get("sort") else sort,
            per_page=30,
            can_view_clinical=can_view_clinical,
            can_view_finance=can_view_finance,
        )

    return {
        "directory": directory,
        "drawer_title": title,
        "drawer_subtitle": subtitle,
        "PatientService": PatientService,
        "can_view_clinical": can_view_clinical,
        "can_view_finance": can_view_finance,
        "can_manage_appointments": can_manage_appointments,
        "can_start_visit": can_start_visit,
        "drawer_query": q,
        "drawer_sort": sort,
        "drawer_cohort": cohort,
        "drawer_journey": journey if journey in Journey.VALID_TYPES and can_view_clinical else "",
        "drawer_period": period,
        "drawer_segment": segment or "",
    }


def _get_patient_workspace_investigation_context(patient):
    active_presets = InvestigationPresetService.list_active_presets()
    selected_preset = None
    missing_workup_tests = []

    selected_preset_id = request.args.get("preset_id", type=int)
    if selected_preset_id:
        selected_preset = next(
            (preset for preset in active_presets if preset.id == selected_preset_id),
            None,
        )

        if selected_preset:
            missing_workup_tests = InvestigationPresetService.missing_tests_for_patient(
                preset=selected_preset,
                patient=patient,
            )

    return {
        "pending_investigation_items": InvestigationService.list_pending_order_items(patient),
        "latest_investigation_results": InvestigationService.list_latest_results(patient),
        "pending_investigation_reviews": InvestigationService.list_patient_pending_results(patient),
        "investigation_presets": active_presets,
        "selected_investigation_preset": selected_preset,
        "missing_workup_tests": missing_workup_tests,
        "can_manage_investigations": RBACService.user_has_permission(current_user, "investigations.manage"),
        "can_review_investigation_results": RBACService.user_has_permission(current_user, "investigation_results.review"),
    }


def _get_patient_workspace_documents_context(patient):
    can_view_documents = RBACService.user_has_permission(current_user, "documents.view")
    can_manage_documents = RBACService.user_has_permission(current_user, "documents.manage")

    if not can_view_documents:
        return {
            "patient_documents": [],
            "can_view_documents": False,
            "can_manage_documents": False,
        }

    return {
        "patient_documents": DocumentService.list_patient_documents(patient),
        "can_view_documents": can_view_documents,
        "can_manage_documents": can_manage_documents,
    }



def _get_patient_workspace_ultrasound_context(patient):
    can_view_ultrasounds = RBACService.user_has_permission(current_user, "ultrasound.view")
    can_manage_ultrasounds = RBACService.user_has_permission(current_user, "ultrasound.manage")

    if not can_view_ultrasounds:
        return {
            "recent_clinic_ultrasounds": [],
            "recent_external_ultrasound_requests": [],
            "recent_external_ultrasound_results": [],
            "can_view_ultrasounds": False,
            "can_manage_ultrasounds": False,
        }

    return {
        "recent_clinic_ultrasounds": ClinicUltrasoundService.list_patient_exams(patient)[:5],
        "recent_external_ultrasound_requests": ExternalUltrasoundService.list_pending_for_patient(patient)[:5],
        "recent_external_ultrasound_results": ExternalUltrasoundService.list_patient_results(patient)[:5],
        "can_view_ultrasounds": can_view_ultrasounds,
        "can_manage_ultrasounds": can_manage_ultrasounds,
        "ClinicUltrasoundService": ClinicUltrasoundService,
    }


def _get_patient_workspace_surgery_context(patient):
    can_view_surgeries = RBACService.user_has_permission(current_user, "surgeries.view")
    can_manage_surgeries = RBACService.user_has_permission(current_user, "surgeries.manage")

    if not can_view_surgeries:
        return {
            "patient_surgeries": [],
            "can_view_surgeries": False,
            "can_manage_surgeries": False,
        }

    return {
        "patient_surgeries": SurgeryService.list_patient_surgeries(patient, limit=8),
        "can_view_surgeries": can_view_surgeries,
        "can_manage_surgeries": can_manage_surgeries,
        "SurgeryService": SurgeryService,
    }


def _get_patient_workspace_partner_context(patient):
    can_view_partners = RBACService.user_has_permission(current_user, "partners.view")
    can_manage_partners = RBACService.user_has_permission(current_user, "partners.manage")

    if not can_view_partners:
        return {
            "partner": None,
            "latest_partner_sa": None,
            "can_view_partners": False,
            "can_manage_partners": False,
        }

    partner = PartnerService.get_patient_partner(patient)
    latest_sa = PartnerSemenAnalysisService.latest_for_partner(partner) if partner else None

    return {
        "partner": partner,
        "latest_partner_sa": latest_sa,
        "can_view_partners": can_view_partners,
        "can_manage_partners": can_manage_partners,
    }


def _get_patient_workspace_finance_context(patient):
    can_view_finance = RBACService.user_has_permission(current_user, "finance.view")

    if not can_view_finance:
        return {
            "can_view_finance": False,
            "patient_finance_summary": None,
            "FinanceService": FinanceService,
        }

    return {
        "can_view_finance": True,
        "patient_finance_summary": FinanceService.get_patient_finance_summary(patient),
        "FinanceService": FinanceService,
    }


@patients_bp.get("/")
@login_required
@RBACService.require_permission("patients.basic.view")
def index():
    period = request.args.get("period", "6m")
    return render_template(
        "patients/index.html",
        **_patient_directory_context(),
        kpis=PatientDashboardService.get_kpis(
            can_view_clinical=RBACService.user_has_permission(current_user, "clinical.view"),
            can_view_finance=RBACService.user_has_permission(current_user, "finance.view"),
        ),
        analytics=PatientDashboardService.get_analytics(
            period=period,
            can_view_clinical=RBACService.user_has_permission(current_user, "clinical.view"),
            can_view_finance=RBACService.user_has_permission(current_user, "finance.view"),
        ),
    )


@patients_bp.get("/search")
@login_required
@RBACService.require_permission("patients.basic.view")
def search():
    return render_template(
        "patients/_search_results.html",
        **_patient_directory_context(),
    )


@patients_bp.get("/global-search")
@login_required
@RBACService.require_permission("patients.basic.view")
def global_search():
    query = (request.args.get("q") or "").strip()
    directory = None
    if query:
        directory = PatientDashboardService.list_patients(
            q=query,
            status="all",
            page=1,
            per_page=8,
            can_view_clinical=False,
            can_view_finance=False,
        )
    return render_template(
        "patients/_global_search_results.html",
        query=query,
        directory=directory,
        PatientService=PatientService,
    )


@patients_bp.get("/quick-list")
@login_required
@RBACService.require_permission("patients.basic.view")
def quick_list():
    return render_template(
        "patients/_quick_list.html",
        **_patient_quick_list_context(request.args.get("cohort", "active")),
    )


@patients_bp.route("/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("patients.basic.create")
def new():
    form = PatientForm()

    if form.validate_on_submit():
        duplicate_patients = PatientService.find_duplicate_phone_patients(
            form.phone_primary.data
        )

        patient = PatientService.create_patient(
            name_ar=form.name_ar.data,
            name_en=form.name_en.data,
            phone_primary=form.phone_primary.data,
            phone_secondary=form.phone_secondary.data,
            email=form.email.data,
            date_of_birth=form.date_of_birth.data,
            age_years_at_registration=form.age_years_at_registration.data,
            marital_status=form.marital_status.data,
            is_virgin=form.is_virgin.data,
            occupation=form.occupation.data,
            governorate=form.governorate.data,
            city=form.city.data,
            street=form.street.data,
        )

        if duplicate_patients:
            flash(
                "Patient created. Warning: another patient already uses this phone number.",
                "warning",
            )
        else:
            flash("Patient created.", "success")

        return redirect(url_for("patients.detail", patient_uuid=patient.uuid))

    return render_template(
        "patients/new.html",
        form=form,
        duplicate_patients=[],
    )


@patients_bp.get("/<patient_uuid>")
@login_required
@RBACService.require_permission("patients.basic.view")
def detail(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()

    investigation_context = _get_patient_workspace_investigation_context(patient)
    documents_context = _get_patient_workspace_documents_context(patient)
    ultrasound_context = _get_patient_workspace_ultrasound_context(patient)
    surgery_context = _get_patient_workspace_surgery_context(patient)
    partner_context = _get_patient_workspace_partner_context(patient)
    finance_context = _get_patient_workspace_finance_context(patient)

    return render_template(
        "patients/detail.html",
        patient=patient,
        PatientService=PatientService,
        JourneyService=JourneyService,
        VisitService=VisitService,
        TimelineService=TimelineService,
        timeline_events=TimelineService.get_patient_timeline(patient),
        **investigation_context,
        **ultrasound_context,
        **documents_context,
        **surgery_context,
        **partner_context,
        **finance_context,
    )


@patients_bp.route("/<patient_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("patients.basic.view")
def edit(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()
    form = PatientForm(obj=patient)

    if form.validate_on_submit():
        duplicate_patients = PatientService.find_duplicate_phone_patients(
            form.phone_primary.data,
            exclude_patient_id=patient.id,
        )

        PatientService.update_patient(
            patient,
            name_ar=form.name_ar.data,
            name_en=form.name_en.data,
            phone_primary=form.phone_primary.data,
            phone_secondary=form.phone_secondary.data,
            email=form.email.data,
            date_of_birth=form.date_of_birth.data,
            age_years_at_registration=form.age_years_at_registration.data,
            marital_status=form.marital_status.data,
            is_virgin=form.is_virgin.data,
            occupation=form.occupation.data,
            governorate=form.governorate.data,
            city=form.city.data,
            street=form.street.data,
        )

        if duplicate_patients:
            flash(
                "Patient updated. Warning: another patient already uses this phone number.",
                "warning",
            )
        else:
            flash("Patient updated.", "success")

        return redirect(url_for("patients.detail", patient_uuid=patient.uuid))

    return render_template(
        "patients/edit.html",
        form=form,
        mrn_form=MRNChangeForm(medical_file_number=patient.medical_file_number),
        patient=patient,
        PatientService=PatientService,
        can_edit_mrn=RBACService.user_has_permission(current_user, "admin.access"),
    )


@patients_bp.post("/<patient_uuid>/mrn")
@login_required
@RBACService.require_permission("admin.access")
def change_mrn(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()
    form = MRNChangeForm()

    if not form.validate_on_submit():
        flash("MRN change was not confirmed.", "danger")
        return redirect(url_for("patients.edit", patient_uuid=patient.uuid))

    try:
        PatientService.change_medical_file_number(
            patient,
            form.medical_file_number.data,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("patients.edit", patient_uuid=patient.uuid))

    flash("Medical file number changed.", "warning")
    return redirect(url_for("patients.detail", patient_uuid=patient.uuid))


@patients_bp.post("/<patient_uuid>/deactivate")
@login_required
@RBACService.require_permission("admin.access")
def deactivate(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()

    PatientService.update_patient(
        patient,
        is_active=False,
        name_ar=patient.name_ar,
        name_en=patient.name_en,
        phone_primary=patient.phone_primary,
        date_of_birth=patient.date_of_birth,
        age_years_at_registration=patient.age_years_at_registration,
        marital_status=patient.marital_status,
    )

    flash("Patient deactivated.", "warning")
    return redirect(url_for("patients.detail", patient_uuid=patient.uuid))

@patients_bp.route("/<patient_uuid>/appointments/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("appointments.manage")
def new_appointment(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()
    form = AppointmentForm()

    if request.method == "GET":
        form.patient_id.data = str(patient.id)
        form.patient_mode.data = "existing"

    if form.validate_on_submit():
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

        flash("Appointment booked.", "success")
        return redirect(url_for("appointments.detail", appointment_uuid=appointment.uuid))

    return render_template(
        "appointments/new.html",
        form=form,
        patient=patient,
        patients=[],
        patient_query="",
        PatientService=PatientService,
        can_create_patient=False,
    )


@patients_bp.get("/<patient_uuid>/appointments")
@login_required
@RBACService.require_permission("appointments.view")
def appointments(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid).first_or_404()
    patient_appointments = AppointmentService.get_patient_appointments(patient.id)

    return render_template(
        "appointments/patient_appointments.html",
        patient=patient,
        appointments=patient_appointments,
        AppointmentService=AppointmentService,
        PatientService=PatientService,
    )

