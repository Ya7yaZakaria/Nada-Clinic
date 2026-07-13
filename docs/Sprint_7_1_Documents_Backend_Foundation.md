# Sprint 7.1 — Documents Backend Foundation

## Goal
Create the backend foundation for patient document storage.

## Scope
- PatientDocument model.
- DocumentService.
- Local file storage helper.
- Secure filename generation.
- File validation.
- Save document metadata.
- Save file to local storage.
- List patient documents.
- Archive document.
- Optional link to Visit.
- Optional link to InvestigationResult.
- RBAC permissions.
- Migration.
- Tests.

## Out of Scope
- UI.
- Routes.
- Forms.
- OCR.
- AI extraction.
- Cloud storage.
- Drawing tools.
- Ultrasound module.
- PDF generation.

## Architecture
- File bytes are stored locally under `instance/uploads/patient_documents/` by default.
- Database stores metadata only.
- Patient remains the root entity.
- Documents can optionally link to Visit and InvestigationResult.
- Existing Stage 6 investigation attachment placeholders are preserved.

## Permissions
- `documents.view`
- `documents.manage`

Admin and Doctor receive both permissions.
Reception remains blocked initially.

## Verification
- `flask db upgrade`
- `flask db current`
- `flask db heads`
- `python -m pytest tests/test_document_model.py -q`
- `python -m pytest tests/test_document_service.py -q`
- `python -m pytest`

## Next
Sprint 7.2 — Patient Documents UI.
