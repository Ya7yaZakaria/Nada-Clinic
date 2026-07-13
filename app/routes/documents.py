from pathlib import Path

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from app.forms.document_forms import DocumentUploadForm
from app.models import InvestigationResult, Patient, PatientDocument
from app.services.document_service import DocumentService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService


documents_bp = Blueprint("documents", __name__)


def _get_patient_or_404(patient_uuid):
    return Patient.query.filter_by(uuid=patient_uuid).first_or_404()


def _get_investigation_result_or_404(result_uuid):
    return InvestigationResult.query.filter_by(uuid=result_uuid).first_or_404()


def _get_document_or_404(document_uuid, include_inactive=False):
    document = DocumentService.get_document(document_uuid, include_inactive=include_inactive)

    if not document:
        abort(404)

    return document


@documents_bp.get("/patients/<patient_uuid>/documents")
@login_required
@RBACService.require_permission("documents.view")
def patient_documents(patient_uuid):
    patient = _get_patient_or_404(patient_uuid)
    documents = DocumentService.list_patient_documents(patient)

    return render_template(
        "documents/index.html",
        patient=patient,
        documents=documents,
        PatientService=PatientService,
        can_manage_documents=RBACService.user_has_permission(current_user, "documents.manage"),
    )


@documents_bp.route("/patients/<patient_uuid>/documents/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("documents.manage")
def new_patient_document(patient_uuid):
    patient = _get_patient_or_404(patient_uuid)
    form = DocumentUploadForm()

    if form.validate_on_submit():
        try:
            document = DocumentService.save_uploaded_file(
                patient=patient,
                file_storage=form.file.data,
                document_type=form.document_type.data,
                title=form.title.data,
                description=form.description.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "documents/new.html",
                patient=patient,
                form=form,
                PatientService=PatientService,
            )

        flash("Document uploaded.", "success")
        return redirect(url_for("documents.detail", document_uuid=document.uuid))

    return render_template(
        "documents/new.html",
        patient=patient,
        form=form,
        PatientService=PatientService,
    )


@documents_bp.get("/documents/<document_uuid>")
@login_required
@RBACService.require_permission("documents.view")
def detail(document_uuid):
    document = _get_document_or_404(document_uuid)

    return render_template(
        "documents/detail.html",
        document=document,
        PatientService=PatientService,
        can_manage_documents=RBACService.user_has_permission(current_user, "documents.manage"),
    )


@documents_bp.get("/documents/<document_uuid>/download")
@login_required
@RBACService.require_permission("documents.view")
def download(document_uuid):
    document = _get_document_or_404(document_uuid)
    path = Path(document.storage_path)

    if not path.exists() or not path.is_file():
        flash("Stored document file was not found.", "danger")
        return redirect(url_for("documents.detail", document_uuid=document.uuid))

    storage_root = DocumentService.get_storage_root().resolve()

    try:
        resolved_path = path.resolve()
        resolved_path.relative_to(storage_root)
    except ValueError:
        abort(403)

    return send_file(
        resolved_path,
        as_attachment=True,
        download_name=document.original_filename,
        mimetype=document.mime_type or "application/octet-stream",
    )


@documents_bp.post("/documents/<document_uuid>/archive")
@login_required
@RBACService.require_permission("documents.manage")
def archive(document_uuid):
    document = _get_document_or_404(document_uuid)

    DocumentService.archive_document(document, actor_user=current_user)

    flash("Document archived.", "warning")
    return redirect(url_for("documents.patient_documents", patient_uuid=document.patient.uuid))


@documents_bp.route("/investigations/results/<result_uuid>/documents/new", methods=["GET", "POST"])
@login_required
@RBACService.require_permission("documents.manage")
def new_investigation_result_document(result_uuid):
    result = _get_investigation_result_or_404(result_uuid)
    form = DocumentUploadForm()

    if request.method == "GET":
        form.document_type.data = PatientDocument.TYPE_INVESTIGATION_REPORT
        if not form.title.data:
            form.title.data = f"{result.test.name_en} report"

    if form.validate_on_submit():
        try:
            document = DocumentService.save_uploaded_file(
                patient=result.patient,
                visit=result.result_visit,
                investigation_result=result,
                file_storage=form.file.data,
                document_type=form.document_type.data or PatientDocument.TYPE_INVESTIGATION_REPORT,
                title=form.title.data,
                description=form.description.data,
                actor_user=current_user,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "documents/new_investigation_result.html",
                result=result,
                patient=result.patient,
                form=form,
                PatientService=PatientService,
            )

        # Preserve Stage 6 placeholder compatibility while linking a real document.
        result.has_attachment = True
        if not result.attachment_label:
            result.attachment_label = document.title
        if not result.external_report_reference:
            result.external_report_reference = document.original_filename

        from app.extensions import db
        db.session.commit()

        flash("Investigation result document uploaded.", "success")
        if result.order_item:
            return redirect(url_for("investigations.detail", order_uuid=result.order_item.order.uuid))

        return redirect(url_for("investigations.patient_orders", patient_uuid=result.patient.uuid))

    return render_template(
        "documents/new_investigation_result.html",
        result=result,
        patient=result.patient,
        form=form,
        PatientService=PatientService,
    )

