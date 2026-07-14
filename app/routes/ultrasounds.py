from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user, login_required

from app.forms.ultrasound_forms import (
    ClinicUltrasoundForm,
    ExternalUltrasoundRequestForm,
    ExternalUltrasoundResultForm,
)
from app.models import PatientDocument, Visit
from app.services.clinic_ultrasound_service import ClinicUltrasoundService
from app.services.document_service import DocumentService
from app.services.external_ultrasound_service import ExternalUltrasoundService
from app.services.rbac_service import RBACService

ultrasounds_bp = Blueprint("ultrasounds", __name__)


def _get_visit_or_404(visit_uuid):
    return Visit.query.filter_by(uuid=visit_uuid).first_or_404()


def _get_external_request_or_404(request_uuid):
    request_record = ExternalUltrasoundService.get_request(request_uuid)
    if not request_record:
        from flask import abort
        abort(404)
    return request_record


def _save_external_ultrasound_document(visit, form):
    if not form.has_file():
        return None

    document_type = form.document_type.data or PatientDocument.TYPE_ULTRASOUND_REPORT

    return DocumentService.save_uploaded_file(
        patient=visit.patient,
        visit=visit,
        file_storage=form.file.data,
        document_type=document_type,
        title=form.title.data or None,
        description=form.result_note.data,
        actor_user=current_user,
    )


@ultrasounds_bp.post("/visits/<visit_uuid>/ultrasounds")
@login_required
@RBACService.require_permission("ultrasound.manage")
def create_from_visit(visit_uuid):
    visit = _get_visit_or_404(visit_uuid)
    form = ClinicUltrasoundForm()

    if not form.validate_on_submit():
        flash("Invalid ultrasound form.", "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    try:
        ClinicUltrasoundService.create_exam(
            visit=visit,
            exam_type=form.exam_type.data,
            exam_route=form.exam_route.data,
            findings_json=form.build_findings_json(),
            findings_text=form.findings_text.data,
            extra_note=form.extra_note.data,
            impression=form.impression.data,
            sketch_note=form.sketch_note.data,
            actor_user=current_user,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    flash("Ultrasound saved.", "success")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))


@ultrasounds_bp.post("/ultrasounds/<ultrasound_uuid>/edit")
@login_required
@RBACService.require_permission("ultrasound.manage")
def edit_inline(ultrasound_uuid):
    exam = ClinicUltrasoundService.get_exam(ultrasound_uuid)
    if not exam:
        flash("Ultrasound exam not found.", "danger")
        return redirect(url_for("patients.index"))

    visit = exam.visit
    form = ClinicUltrasoundForm()

    if not form.validate_on_submit():
        flash("Invalid ultrasound form.", "danger")
        return redirect(
            url_for(
                "visits.detail",
                visit_uuid=visit.uuid,
                edit_ultrasound=exam.uuid,
            )
        )

    try:
        ClinicUltrasoundService.update_exam(
            exam,
            exam_type=form.exam_type.data,
            exam_route=form.exam_route.data,
            findings_json=form.build_findings_json(),
            findings_text=form.findings_text.data,
            extra_note=form.extra_note.data,
            impression=form.impression.data,
            sketch_note=form.sketch_note.data,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(
            url_for(
                "visits.detail",
                visit_uuid=visit.uuid,
                edit_ultrasound=exam.uuid,
            )
        )

    flash("Ultrasound updated.", "success")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))


@ultrasounds_bp.post("/ultrasounds/<ultrasound_uuid>/archive")
@login_required
@RBACService.require_permission("ultrasound.manage")
def archive(ultrasound_uuid):
    exam = ClinicUltrasoundService.get_exam(ultrasound_uuid)

    if not exam:
        flash("Ultrasound exam not found.", "danger")
        return redirect(url_for("patients.index"))

    visit = exam.visit
    ClinicUltrasoundService.archive_exam(exam, actor_user=current_user)

    flash("Ultrasound archived.", "warning")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))


@ultrasounds_bp.post("/visits/<visit_uuid>/external-ultrasounds/requests")
@login_required
@RBACService.require_permission("ultrasound.manage")
def create_external_request(visit_uuid):
    visit = _get_visit_or_404(visit_uuid)
    form = ExternalUltrasoundRequestForm()

    if not form.validate_on_submit():
        flash("Invalid external ultrasound request.", "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    try:
        ExternalUltrasoundService.create_request(
            visit=visit,
            request_note=form.request_note.data,
            categories=form.categories.data,
            modalities=form.modalities.data,
            actor_user=current_user,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    flash("External ultrasound request saved.", "success")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))


@ultrasounds_bp.post("/visits/<visit_uuid>/external-ultrasounds/results")
@login_required
@RBACService.require_permission("ultrasound.manage")
def create_external_result(visit_uuid):
    visit = _get_visit_or_404(visit_uuid)
    pending_requests = ExternalUltrasoundService.list_pending_for_patient(visit.patient)

    form = ExternalUltrasoundResultForm()
    form.set_request_choices(pending_requests)

    if not form.validate_on_submit():
        flash("Add a file or write a doctor review note.", "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    selected_request = None

    if form.request_uuid.data:
        selected_request = ExternalUltrasoundService.get_request(form.request_uuid.data)
        if not selected_request or selected_request.patient_id != visit.patient_id:
            flash("Selected external ultrasound request is invalid.", "danger")
            return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    try:
        document = _save_external_ultrasound_document(visit, form)

        if selected_request:
            ExternalUltrasoundService._complete_request(
                request=selected_request,
                result_visit=visit,
                result_document=document,
                result_note=form.result_note.data,
                actor_user=current_user,
            )
        else:
            ExternalUltrasoundService.create_direct_result(
                visit=visit,
                result_document=document,
                result_note=form.result_note.data,
                categories=form.categories.data,
                modalities=form.modalities.data,
                actor_user=current_user,
            )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    flash("External ultrasound result saved.", "success")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))


@ultrasounds_bp.post("/visits/<visit_uuid>/external-ultrasounds/requests/<request_uuid>/result")
@login_required
@RBACService.require_permission("ultrasound.manage")
def complete_external_request_from_visit(visit_uuid, request_uuid):
    visit = _get_visit_or_404(visit_uuid)
    external_request = _get_external_request_or_404(request_uuid)
    form = ExternalUltrasoundResultForm()

    if not form.validate_on_submit():
        flash("Add a file or write a doctor review note.", "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    if external_request.patient_id != visit.patient_id:
        flash("External ultrasound request does not belong to this patient.", "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    try:
        document = _save_external_ultrasound_document(visit, form)
        ExternalUltrasoundService._complete_request(
            request=external_request,
            result_visit=visit,
            result_document=document,
            result_note=form.result_note.data,
            actor_user=current_user,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    flash("External ultrasound request completed.", "success")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))


@ultrasounds_bp.post("/external-ultrasounds/requests/<request_uuid>/cancel")
@login_required
@RBACService.require_permission("ultrasound.manage")
def cancel_external_request(request_uuid):
    external_request = _get_external_request_or_404(request_uuid)
    visit = external_request.requested_visit

    try:
        ExternalUltrasoundService.cancel_request(external_request)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("visits.detail", visit_uuid=visit.uuid))

    flash("External ultrasound request cancelled.", "warning")
    return redirect(url_for("visits.detail", visit_uuid=visit.uuid))
