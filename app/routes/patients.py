from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.patient_forms import MRNChangeForm, PatientForm
from app.models import Patient
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


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

    return render_template(
        "patients/detail.html",
        patient=patient,
        PatientService=PatientService,
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
