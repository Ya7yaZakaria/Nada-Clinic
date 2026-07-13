# Sprint 6.4 — Result Review + Patient Workspace

## Goal
Allow doctors to review entered investigation results and surface investigation data inside Patient Workspace.

## Scope
- Result review form.
- Pending result review page.
- Review POST workflow.
- Reviewed status.
- Reviewed by doctor.
- Reviewed at timestamp.
- Review note.
- Abnormal flag confirmation.
- Patient Workspace pending ordered results.
- Patient Workspace pending review results.
- Patient Workspace latest results.
- Patient Workspace missing workup from preset.
- Generated timeline investigation events.
- Service/UI tests.

## Out of Scope
- AI interpretation.
- Automatic diagnosis.
- Patient notifications.
- Advanced alerts.
- Lab integration.
- Complex reference ranges.
- Real upload/storage.
- Print request.

## Routes
- GET /investigations/pending
- POST /investigations/results/<result_uuid>/review
- GET /patients/<patient_uuid>?preset_id=<preset_id>

## Acceptance Criteria
- Doctor can review result.
- Review stores reviewed_by_user, reviewed_at, review_note.
- Abnormal flag can be confirmed.
- Pending results disappear after review.
- Latest results appear in Patient Workspace.
- Missing workup can be shown from preset.
- Timeline includes investigation result and reviewed events.
- Reception cannot review.
- Full test suite passes.
- No migration drift.
