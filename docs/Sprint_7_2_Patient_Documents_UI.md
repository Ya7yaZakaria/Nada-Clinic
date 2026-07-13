# Sprint 7.2 — Patient Documents UI

## Goal
Allow Doctor/Admin users to upload, view, download, and archive patient documents from the UI.

## Scope
- Documents blueprint/routes.
- DocumentUploadForm.
- Patient documents list.
- Upload form.
- Document detail page.
- Download route.
- Archive route.
- Patient Workspace documents section.
- UI tests.
- Documentation.

## Out of Scope
- OCR.
- AI extraction.
- Cloud storage.
- Drawing/annotation.
- Ultrasound structured module.
- Investigation result attachment UI.

## Permissions
Uses:
- documents.view
- documents.manage

Admin and Doctor can use document workflows.
Reception remains blocked initially.

## Routes
- GET /patients/<patient_uuid>/documents
- GET /patients/<patient_uuid>/documents/new
- POST /patients/<patient_uuid>/documents/new
- GET /documents/<document_uuid>
- GET /documents/<document_uuid>/download
- POST /documents/<document_uuid>/archive

## Verification
- python -m pytest tests/test_document_ui.py -q
- python -m pytest tests/test_document_model.py tests/test_document_service.py tests/test_document_ui.py -q
- python -m pytest

## Next
Sprint 7.3 — Attach Documents to Investigation Results.
