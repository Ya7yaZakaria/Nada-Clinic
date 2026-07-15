from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.appointment_forms import AppointmentForm

from app.forms.patient_forms import MRNChangeForm, PatientForm
from app.models import Patient
from app.services.appointment_service import AppointmentService
from app.services.clinic_ultrasound_service import ClinicUltrasoundService
from app.services.external_ultrasound_service import ExternalUltrasoundService
from app.services.document_service import DocumentService
from app.services.investigation_preset_service import InvestigationPresetService
from app.services.investigation_service import InvestigationService
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.partner_service import PartnerService
from app.services.partner_semen_analysis_service import PartnerSemenAnalysisService
from app.services.rbac_service import RBACService
from app.services.surgery_service import SurgeryService
from app.services.timeline_service import TimelineService
from app.services.visit_service import VisitService

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


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


@patients_bp.get("/")
@login_required
@RBACService.require_permission("patients.basic.view")
def index():
    patients = PatientService.get_recent_patients(limit=10)

    return render_template(
        "patients/index.html",
        patients=patients,
        PatientService=PatientService,
    )


@patients_bp.get("/search")
@login_required
@RBACService.require_permission("patients.basic.view")
def search():
    query = request.args.get("q", "")
    patients = PatientService.search_patients(query, limit=20)

    return render_template(
        "patients/_search_results.html",
        patients=patients,
        query=query,
        PatientService=PatientService,
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

    if form.validate_on_submit():
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
            duration_minutes=form.duration_minutes.data,
            appointment_type=form.appointment_type.data,
            source=form.source.data,
            notes=form.notes.data,
        )

        flash("Appointment booked.", "success")
        return redirect(url_for("appointments.detail", appointment_uuid=appointment.uuid))

    return render_template(
        "appointments/new.html",
        form=form,
        patient=patient,
        patients=[],
        patient_query="",
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

