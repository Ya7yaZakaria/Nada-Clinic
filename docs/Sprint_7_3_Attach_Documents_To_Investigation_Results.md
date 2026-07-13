# Sprint 7.3 — Attach Documents to Investigation Results

## Goal
Use the Documents module to attach real uploaded files to Investigation Results.

## Scope
- Upload document from investigation result context.
- Link PatientDocument to InvestigationResult.
- Preserve Stage 6 placeholder fields.
- Show attached reports on investigation order detail.
- Show attached reports on patient investigations page.
- Improve document detail result link.
- Add tests.

## Out of Scope
- OCR.
- AI extraction.
- Lab integration.
- Result interpretation.
- PDF parsing.
- Drawing/annotation.
- Cloud storage.

## Routes
- GET /investigations/results/<result_uuid>/documents/new
- POST /investigations/results/<result_uuid>/documents/new

## Verification
- python -m pytest tests/test_investigation_document_attachment.py -q
- python -m pytest tests/test_document_ui.py tests/test_investigation_document_attachment.py -q
- python -m pytest

## Next
Sprint 7.4 — Documents & Storage Freeze Review.
