from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.forms.partner_forms import PartnerForm, PartnerPrescriptionForm, PartnerSemenAnalysisForm
from app.forms.prescription_forms import PrescriptionItemForm
from app.models import Patient
from app.models.drug_dictionary import DrugRoute
from app.models.prescription import PrescriptionItem
from app.services.drug_dictionary_service import DrugDictionaryService
from app.services.drug_service import DrugService
from app.services.partner_semen_analysis_service import PartnerSemenAnalysisService
from app.services.partner_service import PartnerService
from app.services.patient_service import PatientService
from app.services.prescription_service import PrescriptionService
from app.services.rbac_service import RBACService

partners_bp = Blueprint("partners", __name__)


def _get_partner_or_404(partner_uuid):
    partner = PartnerService.get_partner(partner_uuid)
    if not partner:
        from flask import abort
        abort(404)
    return partner


def _choice_label(item):
    if getattr(item, "name_ar", None):
        return f"{item.name_en} / {item.name_ar}"
    return item.name_en


def _drug_choice_label(drug):
    form_name = drug.form.name_en if drug.form else "-"
    return f"{drug.trade_name} {drug.strength} - {drug.generic_name} ({form_name})"


def _populate_prescription_item_form(form):
    form.drug_id.choices = [(0, "Select drug...")] + [
        (drug.id, _drug_choice_label(drug))
        for drug in DrugService.get_active_drugs()
    ]
    form.route_id.choices = [(0, "Use drug default route")] + [
        (route.id, _choice_label(route))
        for route in DrugDictionaryService.get_active_routes()
    ]


def _get_drug_or_none(drug_id):
    if not drug_id:
        return None
    from app.models.drug import Drug
    return Drug.query.filter_by(id=drug_id, is_active=True).first()


def _get_route_or_none(route_id):
    if not route_id:
        return None
    return DrugRoute.query.filter_by(id=route_id, is_active=True).first()


def _apply_item_to_form(form, item):
    form.drug_id.data = item.drug_id
    form.route_id.data = item.route_id or 0
    form.dose.data = item.dose
    form.frequency.data = item.frequency
    form.duration.data = item.duration
    form.instructions_ar.data = item.instructions_ar


def _ensure_partner_prescription_permission():
    if not RBACService.user_has_permission(current_user, "partners.manage"):
        from flask import abort
        abort(403)
    if not RBACService.user_has_permission(current_user, "prescriptions.manage"):
        from flask import abort
        abort(403)


@partners_bp.route("/patients/<patient_uuid>/partner/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("partners.manage")
def new_for_patient(patient_uuid):
    patient = Patient.query.filter_by(uuid=patient_uuid, is_active=True).first_or_404()
    form = PartnerForm()

    if form.validate_on_submit():
        try:
            partner = PartnerService.create_partner(
                patient=patient,
                name=form.name.data,
                phone=form.phone.data,
                age_years=form.age_years.data,
                occupation=form.occupation.data,
                previous_children=form.previous_children.data,
                fertility_notes=form.fertility_notes.data,
                medical_notes=form.medical_notes.data,
                follow_up_note=form.follow_up_note.data,
                follow_up_date=form.follow_up_date.data,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("partners/new.html", patient=patient, form=form)

        flash("Partner saved.", "success")
        return redirect(url_for("patients.detail", patient_uuid=patient.uuid))

    return render_template("partners/new.html", patient=patient, form=form)


@partners_bp.route("/partners/<partner_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("partners.manage")
def edit(partner_uuid):
    partner = _get_partner_or_404(partner_uuid)
    form = PartnerForm(obj=partner)

    if form.validate_on_submit():
        try:
            PartnerService.update_partner(
                partner,
                name=form.name.data,
                phone=form.phone.data,
                age_years=form.age_years.data,
                occupation=form.occupation.data,
                previous_children=form.previous_children.data,
                fertility_notes=form.fertility_notes.data,
                medical_notes=form.medical_notes.data,
                follow_up_note=form.follow_up_note.data,
                follow_up_date=form.follow_up_date.data,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("partners/edit.html", partner=partner, form=form)

        flash("Partner updated.", "success")
        return redirect(url_for("patients.detail", patient_uuid=partner.patient.uuid))

    return render_template("partners/edit.html", partner=partner, form=form)


@partners_bp.get("/partners/<partner_uuid>")
@login_required
@RBACService.require_permission("partners.view")
def detail(partner_uuid):
    partner = _get_partner_or_404(partner_uuid)
    latest_sa = PartnerSemenAnalysisService.latest_for_partner(partner)
    analyses = PartnerSemenAnalysisService.list_partner_analyses(partner)
    prescriptions = PrescriptionService.list_partner_prescriptions(partner)

    return render_template(
        "partners/detail.html",
        partner=partner,
        latest_sa=latest_sa,
        analyses=analyses,
        prescriptions=prescriptions,
        PatientService=PatientService,
    )


@partners_bp.route("/partners/<partner_uuid>/semen-analysis/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("partners.manage")
def new_semen_analysis(partner_uuid):
    partner = _get_partner_or_404(partner_uuid)
    if not RBACService.user_has_permission(current_user, "documents.manage"):
        from flask import abort
        abort(403)

    form = PartnerSemenAnalysisForm()

    if form.validate_on_submit():
        try:
            PartnerSemenAnalysisService.create_analysis(
                partner=partner,
                analysis_date=form.analysis_date.data,
                notes=form.notes.data,
                file_storage=form.file.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("partners/semen_analysis_new.html", partner=partner, form=form)

        flash("Semen analysis saved.", "success")
        return redirect(url_for("partners.semen_analysis_list", partner_uuid=partner.uuid))

    return render_template("partners/semen_analysis_new.html", partner=partner, form=form)


@partners_bp.get("/partners/<partner_uuid>/semen-analysis")
@login_required
@RBACService.require_permission("partners.view")
def semen_analysis_list(partner_uuid):
    partner = _get_partner_or_404(partner_uuid)
    analyses = PartnerSemenAnalysisService.list_partner_analyses(partner)

    return render_template(
        "partners/semen_analysis_list.html",
        partner=partner,
        analyses=analyses,
    )


@partners_bp.get("/partners/semen-analysis/<sa_uuid>")
@login_required
@RBACService.require_permission("partners.view")
def semen_analysis_detail(sa_uuid):
    analysis = PartnerSemenAnalysisService.get_analysis(sa_uuid)
    if not analysis:
        from flask import abort
        abort(404)

    return render_template("partners/semen_analysis_detail.html", analysis=analysis)


@partners_bp.post("/partners/semen-analysis/<sa_uuid>/archive")
@login_required
@RBACService.require_permission("partners.manage")
def archive_semen_analysis(sa_uuid):
    analysis = PartnerSemenAnalysisService.get_analysis(sa_uuid)
    if not analysis:
        from flask import abort
        abort(404)

    PartnerSemenAnalysisService.archive_analysis(analysis)
    flash("Semen analysis archived.", "warning")
    return redirect(url_for("partners.semen_analysis_list", partner_uuid=analysis.partner.uuid))


@partners_bp.route("/partners/<partner_uuid>/prescriptions/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("partners.manage")
def new_prescription(partner_uuid):
    _ensure_partner_prescription_permission()
    partner = _get_partner_or_404(partner_uuid)
    form = PartnerPrescriptionForm()

    if form.validate_on_submit():
        try:
            prescription = PrescriptionService.create_partner_prescription(
                partner=partner,
                notes=form.notes.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("partners/prescriptions_new.html", partner=partner, form=form)

        flash("Partner prescription created.", "success")
        return redirect(url_for("partners.prescription_detail", prescription_uuid=prescription.uuid))

    return render_template("partners/prescriptions_new.html", partner=partner, form=form)


@partners_bp.get("/partners/<partner_uuid>/prescriptions")
@login_required
@RBACService.require_permission("partners.view")
def prescriptions_list(partner_uuid):
    if not RBACService.user_has_permission(current_user, "prescriptions.view"):
        from flask import abort
        abort(403)
    partner = _get_partner_or_404(partner_uuid)
    prescriptions = PrescriptionService.list_partner_prescriptions(partner)

    return render_template(
        "partners/prescriptions_list.html",
        partner=partner,
        prescriptions=prescriptions,
    )


@partners_bp.get("/partners/prescriptions/<prescription_uuid>")
@login_required
@RBACService.require_permission("partners.view")
def prescription_detail(prescription_uuid):
    if not RBACService.user_has_permission(current_user, "prescriptions.view"):
        from flask import abort
        abort(403)

    prescription = PrescriptionService.get_partner_prescription(prescription_uuid)
    if not prescription:
        from flask import abort
        abort(404)

    item_form = None
    if (
        RBACService.user_has_permission(current_user, "partners.manage")
        and RBACService.user_has_permission(current_user, "prescriptions.manage")
    ):
        item_form = PrescriptionItemForm()
        _populate_prescription_item_form(item_form)

    return render_template(
        "partners/prescription_detail.html",
        prescription=prescription,
        prescription_items=PrescriptionService.list_items(prescription),
        item_form=item_form,
    )


@partners_bp.post("/partners/prescriptions/<prescription_uuid>/items")
@login_required
@RBACService.require_permission("partners.manage")
def add_prescription_item(prescription_uuid):
    _ensure_partner_prescription_permission()
    prescription = PrescriptionService.get_partner_prescription(prescription_uuid)
    if not prescription:
        from flask import abort
        abort(404)

    form = PrescriptionItemForm()
    _populate_prescription_item_form(form)

    if not form.validate_on_submit():
        flash("Invalid prescription item.", "danger")
        return redirect(url_for("partners.prescription_detail", prescription_uuid=prescription.uuid))

    drug = _get_drug_or_none(form.drug_id.data)
    route = _get_route_or_none(form.route_id.data)

    try:
        PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose=form.dose.data,
            frequency=form.frequency.data,
            duration=form.duration.data,
            instructions_ar=form.instructions_ar.data,
            route=route,
        )
        PrescriptionService.update_prescription(prescription, actor_user=current_user)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("partners.prescription_detail", prescription_uuid=prescription.uuid))

    flash("Medication added to partner prescription.", "success")
    return redirect(url_for("partners.prescription_detail", prescription_uuid=prescription.uuid))


@partners_bp.route("/partners/prescription-items/<item_uuid>/edit", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("partners.manage")
def edit_prescription_item(item_uuid):
    _ensure_partner_prescription_permission()
    item = PrescriptionItem.query.filter_by(uuid=item_uuid).first_or_404()
    prescription = item.prescription

    if not prescription.is_partner_target:
        from flask import abort
        abort(404)

    form = PrescriptionItemForm()
    _populate_prescription_item_form(form)

    if form.validate_on_submit():
        drug = _get_drug_or_none(form.drug_id.data)
        route = _get_route_or_none(form.route_id.data)

        try:
            PrescriptionService.update_item(
                item,
                drug=drug,
                dose=form.dose.data,
                frequency=form.frequency.data,
                duration=form.duration.data,
                instructions_ar=form.instructions_ar.data,
                route=route,
            )
            PrescriptionService.update_prescription(prescription, actor_user=current_user)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("partners/prescription_item_form.html", form=form, item=item)

        flash("Partner medication updated.", "success")
        return redirect(url_for("partners.prescription_detail", prescription_uuid=prescription.uuid))

    if item.drug_id and not form.drug_id.data:
        _apply_item_to_form(form, item)

    return render_template("partners/prescription_item_form.html", form=form, item=item)


@partners_bp.post("/partners/prescription-items/<item_uuid>/remove")
@login_required
@RBACService.require_permission("partners.manage")
def remove_prescription_item(item_uuid):
    _ensure_partner_prescription_permission()
    item = PrescriptionItem.query.filter_by(uuid=item_uuid).first_or_404()
    prescription = item.prescription

    if not prescription.is_partner_target:
        from flask import abort
        abort(404)

    PrescriptionService.remove_item(item)
    PrescriptionService.update_prescription(prescription, actor_user=current_user)

    flash("Partner medication removed.", "success")
    return redirect(url_for("partners.prescription_detail", prescription_uuid=prescription.uuid))
