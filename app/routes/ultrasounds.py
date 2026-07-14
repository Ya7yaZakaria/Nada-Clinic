from flask import Blueprint, flash, redirect, url_for
from flask_login import current_user, login_required

from app.forms.ultrasound_forms import ClinicUltrasoundForm
from app.models import Visit
from app.services.clinic_ultrasound_service import ClinicUltrasoundService
from app.services.rbac_service import RBACService

ultrasounds_bp = Blueprint("ultrasounds", __name__)


@ultrasounds_bp.post("/visits/<visit_uuid>/ultrasounds")
@login_required
@RBACService.require_permission("ultrasound.manage")
def create_from_visit(visit_uuid):
    visit = Visit.query.filter_by(uuid=visit_uuid).first_or_404()
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
