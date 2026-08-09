# Stages 07 08 Documents Ultrasound

Historical sprint/stage source material consolidated verbatim. It is retained for traceability and does not override current code.

## Included legacy sources

- `Sprint_7_1_Documents_Backend_Foundation.md`
- `Sprint_7_2_Patient_Documents_UI.md`
- `Sprint_7_3_Attach_Documents_To_Investigation_Results.md`
- `Sprint_8_1_Ultrasound_Backend_Foundation.md`
- `Sprint_8_2_Inline_Clinic_Ultrasound_Visit_UI.md`
- `Sprint_8_3_External_Ultrasound_Request_Upload.md`
- `Stage_7_Documents_Storage_Freeze_Review.md`
- `Stage_8_Ultrasound_Freeze_Review.md`

---

## Legacy source: `Sprint_7_1_Documents_Backend_Foundation.md`

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

---

## Legacy source: `Sprint_7_2_Patient_Documents_UI.md`

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

---

## Legacy source: `Sprint_7_3_Attach_Documents_To_Investigation_Results.md`

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

---

## Legacy source: `Sprint_8_1_Ultrasound_Backend_Foundation.md`

# Sprint 8.1 — Ultrasound Backend Foundation

## Goal

Create backend foundation for Stage 8 Ultrasound without UI.

## Scope

- ClinicUltrasoundExam model.
- ExternalUltrasoundRequest model.
- ClinicUltrasoundService.
- ExternalUltrasoundService.
- RBAC permissions:
  - ultrasound.view
  - ultrasound.manage
- Alembic migration.
- Model tests.
- Service tests.

## Out of Scope

- UI.
- External upload UI.
- Patient workspace UI.
- Timeline UI.
- Print.
- AI/OCR.
- Canvas sketch.
- Full radiology workflow.

## Key Decisions

- Clinic ultrasound belongs to Visit.
- No exam_date column.
- Ultrasound date is derived from Visit.visit_date.
- Sketch is only sketch_note text.
- External request doctor-facing field is request_note only.
- External result will use PatientDocument in Sprint 8.3.
- No ExternalUltrasoundResult table.

## Models

### ClinicUltrasoundExam

Stores structured ultrasound done inside clinic during a Visit.

### ExternalUltrasoundRequest

Stores lightweight pending/completed/cancelled external ultrasound requests.

## Services

### ClinicUltrasoundService

Handles create, update, archive, list, validation, and summary.

### ExternalUltrasoundService

Handles request creation, cancellation, pending lists, and completion with a PatientDocument.

## Verification

Run:

```
pytest tests/test_clinic_ultrasound_model.py -q
pytest tests/test_clinic_ultrasound_service.py -q
pytest tests/test_external_ultrasound_service.py -q
pytest tests/test_rbac.py -q
pytest
flask db current
flask db heads
git status
git diff --stat
```

## Acceptance Criteria

- ClinicUltrasoundExam table exists.
- ExternalUltrasoundRequest table exists.
- No exam_date column exists.
- Clinic ultrasound date is derived from Visit.visit_date.
- External request stores only request_note as doctor-entered content.
- RBAC permissions are seeded for Admin and Doctor.
- Reception has no ultrasound permissions.
- Tests pass.

---

## Legacy source: `Sprint_8_2_Inline_Clinic_Ultrasound_Visit_UI.md`

# Sprint 8.2 — Inline Clinic Ultrasound Visit UI

## Goal

Allow the doctor to add, view, edit, and archive clinic ultrasound directly inside the Visit Detail page.

## Scope

- Inline Add Clinic Ultrasound form inside Visit Detail.
- Inline Edit Clinic Ultrasound form inside saved ultrasound cards.
- Clinic ultrasound cards inside Visit Detail.
- Light clinic ultrasound summary inside Patient Workspace.
- Type-specific fields for OBS, Gyne, OI/TI, and Other ultrasound.
- Store structured values in `findings_json`.
- Use `Visit.visit_date` for displayed ultrasound date.

## Out of Scope

- External ultrasound request UI.
- External ultrasound result upload UI.
- External result table.
- Separate ultrasound new/edit/detail pages.
- Canvas sketch.
- Print.
- AI/OCR.
- DICOM.
- Growth charts.

## Files Created

- `app/forms/ultrasound_forms.py`
- `app/routes/ultrasounds.py`
- `app/templates/ultrasounds/_clinic_ultrasound_form.html`
- `app/templates/ultrasounds/_clinic_ultrasound_card.html`
- `app/templates/visits/_ultrasound_section.html`
- `app/templates/patients/_ultrasound_section.html`
- `tests/test_clinic_ultrasound_ui.py`

## Files Modified

- `app/__init__.py`
- `app/routes/visits.py`
- `app/routes/patients.py`
- `app/templates/visits/detail.html`
- `app/templates/patients/detail.html`
- `README.md`
- `CHANGELOG.md`
- `MEMORY.md`

## Database Impact

No migration.

## Routes

- `POST /visits/<visit_uuid>/ultrasounds`
- `POST /ultrasounds/<ultrasound_uuid>/edit`
- `POST /ultrasounds/<ultrasound_uuid>/archive`

## Acceptance Criteria

- Doctor can add OBS clinic ultrasound inline from Visit Detail.
- Doctor can add Gyne clinic ultrasound inline from Visit Detail.
- Doctor can add OI/TI clinic ultrasound inline from Visit Detail.
- Doctor can add Other clinic ultrasound inline from Visit Detail.
- Form does not include `exam_date`.
- Form does not include `plan`.
- Ultrasound card displays date from linked Visit.
- Extra note textbox exists.
- Sketch note textbox exists.
- Ultrasound appears in Visit Detail.
- Recent clinic ultrasound appears lightly in Patient Workspace.
- Doctor/Admin can manage.
- Reception cannot manage ultrasound routes.
- Tests pass.

## Verification

```powershell
$env:FLASK_APP = "app"
$env:FLASK_ENV = "development"
$env:PYTHONPATH = (Get-Location).Path

pytest tests/test_clinic_ultrasound_ui.py -q
pytest tests/test_rbac.py -q
pytest
flask db current
flask db heads
flask routes
git status
git diff --stat
```

---

## Legacy source: `Sprint_8_3_External_Ultrasound_Request_Upload.md`

# Sprint 8.3 — External Ultrasound Request + Upload

## Goal

Add external ultrasound request and result workflows inside the Visit Ultrasound section.

## Scope

- Request external ultrasound from Visit.
- Use small inline/collapse request form.
- Support multi-select category: OBS, Gyne, OI/TI, Other.
- Support multi-select modality: 2D, 3D, 4D, Doppler, TVS, TAS.
- Show pending external ultrasound requests.
- Allow uploading result against pending request.
- Allow note-only completion without file.
- Allow direct external ultrasound result without prior request.
- Allow file-only, note-only, or file + note result.
- Show image thumbnail for image uploads.
- Show PDF/file card for non-image uploads.
- Store uploaded files through `PatientDocument`.
- Store doctor review note on `ExternalUltrasoundRequest.result_note`.
- Mark pending request completed after saving result.
- Show external ultrasound requests/results in Patient Workspace.

## Out of Scope

- OCR.
- AI extraction.
- DICOM.
- Growth charts.
- Radiology center module.
- Multiple-file bundle upload.
- Structured external report interpretation.
- Print integration.

## Database Impact

Adds metadata columns to `external_ultrasound_requests`:

- `request_categories_json`
- `request_modalities_json`
- `result_note`

Migration:

- `20260715_0066_external_ultrasound_request_upload_metadata.py`

## Routes

- `POST /visits/<visit_uuid>/external-ultrasounds/requests`
- `POST /visits/<visit_uuid>/external-ultrasounds/results`
- `POST /visits/<visit_uuid>/external-ultrasounds/requests/<request_uuid>/result`
- `POST /external-ultrasounds/requests/<request_uuid>/cancel`
- `GET /documents/<document_uuid>/preview`

## Acceptance Criteria

- Doctor can create external US request from Visit.
- Request supports category/modality multi-select.
- Pending requests appear inside Visit Ultrasound section.
- Doctor can upload file against pending request.
- Doctor can complete pending request with note only.
- Doctor can add direct external US result without pending request.
- Direct result accepts file only, note only, or both.
- Empty result without file and without note is rejected.
- Uploaded image appears as thumbnail.
- PDF appears as file card.
- External results appear in Patient Workspace.
- Reception is blocked from external ultrasound routes.
- Tests pass.

---

## Legacy source: `Stage_7_Documents_Storage_Freeze_Review.md`

# Stage 7 — Documents & Storage Freeze Review

## Status

Stage 7 is ready to freeze after Sprint 7.1, Sprint 7.2, Sprint 7.3, and Sprint 7.3A cleanup verification.

## Scope Reviewed

- PatientDocument model.
- DocumentService.
- Local file storage.
- Secure stored filenames.
- File validation.
- Patient document upload/list/detail/download/archive.
- Patient Workspace document section.
- InvestigationResult document attachment.
- RBAC permissions.
- Tests.
- Documentation.
- Migration state.
- Out-of-scope boundaries.

## Implemented Sprints

### Sprint 7.1 — Documents Backend Foundation

Implemented:
- PatientDocument model.
- Local file storage service.
- File validation.
- Secure stored filename generation.
- Metadata persistence.
- Patient/Visit/InvestigationResult optional links.
- Archive behavior.
- RBAC permissions.
- Backend tests.
- Migration 20260713_0064.

### Sprint 7.2 — Patient Documents UI

Implemented:
- Documents blueprint.
- DocumentUploadForm.
- Patient document list.
- Upload form.
- Document detail.
- Download route.
- Archive route.
- Patient Workspace documents section.
- UI tests.
- Documentation.

### Sprint 7.3 — Attach Documents to Investigation Results

Implemented:
- Upload document from InvestigationResult context.
- Link PatientDocument to InvestigationResult.
- Preserve Stage 6 placeholders:
  - has_attachment
  - attachment_label
  - external_report_reference
- Show attached reports on investigation order detail.
- Show attached reports on patient investigation page.
- Improve document detail link back to investigation result/order.
- Attachment tests.
- Documentation.

### Sprint 7.3A — Pre-Freeze Cleanup

Implemented:
- Removed duplicated Doctor document permissions.
- Removed unused current_app import from documents route.
- Verified RBAC/document/investigation attachment/full suite.

## Model Review

PatientDocument stores metadata only. File bytes are not stored in the database.

Reviewed fields:
- uuid
- patient_id
- visit_id nullable
- investigation_result_id nullable
- document_type
- title
- description
- original_filename
- stored_filename
- storage_path
- mime_type
- file_size
- checksum
- uploaded_by_user_id
- is_active
- created_at
- updated_at

## Migration Review

Current migration head:
- 20260713_0064

No migration drift detected.

Sprint 7.2, Sprint 7.3, and Sprint 7.3A added no migration.

## Service Review

DocumentService reviewed:
- validate_file
- validate_document_type
- generate_stored_filename
- ensure_storage_root
- save_uploaded_file
- create_document_metadata
- get_document
- list_patient_documents
- list_visit_documents
- list_investigation_result_documents
- archive_document

Storage is local and configurable by:
- PATIENT_DOCUMENT_UPLOAD_FOLDER
- PATIENT_DOCUMENT_MAX_FILE_SIZE_BYTES

## Route Review

Document routes reviewed:
- GET /patients/<patient_uuid>/documents
- GET /patients/<patient_uuid>/documents/new
- POST /patients/<patient_uuid>/documents/new
- GET /documents/<document_uuid>
- GET /documents/<document_uuid>/download
- POST /documents/<document_uuid>/archive
- GET /investigations/results/<result_uuid>/documents/new
- POST /investigations/results/<result_uuid>/documents/new

Download route validates resolved path against storage root before sending the file.

## Form Review

DocumentUploadForm reviewed:
- document_type
- title
- description
- file

Allowed extensions:
- pdf
- png
- jpg
- jpeg
- webp
- gif
- txt

## Template Review

Templates reviewed:
- app/templates/documents/index.html
- app/templates/documents/new.html
- app/templates/documents/detail.html
- app/templates/documents/new_investigation_result.html
- app/templates/patients/_documents_section.html
- app/templates/investigations/detail.html
- app/templates/investigations/patient_orders.html

## RBAC Review

Permissions:
- documents.view
- documents.manage

Role access:
- Admin: allowed.
- Doctor: allowed.
- Reception: blocked initially.

## Audit Review

Current audit fields:
- uploaded_by_user_id
- created_at
- updated_at
- is_active

Full audit log remains deferred until a standardized audit module is introduced.

## Security Review

Verified:
- Secure generated stored filenames.
- Extension validation.
- MIME validation.
- File size validation.
- Download path traversal guard.
- RBAC-protected routes.
- Archive instead of hard delete.

Known future hardening:
- Deployment storage backup policy.
- Optional antivirus/file scanning.
- Optional stricter MIME sniffing.
- Storage cleanup policy for orphan files if DB commit fails after file save.

## Out of Scope Confirmed

Not implemented in Stage 7:
- OCR.
- AI extraction.
- AI interpretation.
- Cloud storage.
- Google Drive sync.
- Lab integration.
- DICOM/PACS.
- PDF parsing.
- Drawing/annotation tools.
- Ultrasound structured module.
- Patient portal upload.

## Acceptance Criteria

- Doctor can upload patient document.
- Document is stored locally.
- Metadata is stored in database.
- Document links to Patient.
- Document can optionally link to Visit.
- Document can optionally link to InvestigationResult.
- Patient Workspace shows documents.
- Doctor can view/download document.
- Doctor can archive document.
- Investigation result can have real attached report.
- Reception is blocked.
- No AI/OCR/cloud/drawing added.
- Full test suite passes.
- Migration head is clean.
- Documentation updated.

## Freeze Decision

Stage 7 can be frozen after:
- Sprint 7.3A cleanup is committed.
- This freeze review document is committed.
- Final full suite passes.
- DB current/head remains 20260713_0064.
- Git status is clean after push.

## Next Stage

Stage 8 — Ultrasound.

Stage 8 should reuse Stage 7 documents for:
- ultrasound image attachment
- ultrasound report file
- future drawing overlay linked as structured JSON, not file storage

---

## Legacy source: `Stage_8_Ultrasound_Freeze_Review.md`

# Stage 8 Freeze Review — Ultrasound

## Status

Stage 8 Ultrasound is frozen.

## Completed Sprints

- Sprint 8.1 — Ultrasound Backend Foundation.
- Sprint 8.2 — Inline Clinic Ultrasound UI.
- Sprint 8.3 — External Ultrasound Request + Upload.

## Final Scope

Stage 8 now supports:

- Clinic ultrasound records inside Visit.
- Inline add/edit/archive clinic ultrasound workflow.
- Structured clinic ultrasound fields for OBS, Gyne, and OI/TI.
- External ultrasound request from Visit.
- External US category/modality multi-select.
- Pending external ultrasound request cards.
- External US result upload from Visit.
- External US note-only result.
- Direct external US result without prior request.
- Uploaded image thumbnail preview.
- PDF/file result cards.
- Patient Workspace ultrasound summary.
- Reuse of PatientDocument storage for external reports/images.
- Ultrasound RBAC through `ultrasound.view` and `ultrasound.manage`.

## Out of Scope / Deferred

- OCR.
- AI report extraction.
- DICOM.
- Growth charts.
- Radiology center module.
- Multiple-file bundle upload.
- Structured fetal biometry charts.
- Automatic interpretation.
- AI edits to clinical records.

## Verification

Final verified state before freeze:

- `pytest tests/test_clinic_ultrasound_ui.py -q` → 7 passed.
- `pytest tests/test_external_ultrasound_ui.py -q` → 7 passed.
- `pytest tests/test_external_ultrasound_service.py -q` → 5 passed.
- `pytest tests/test_document_ui.py -q` → 7 passed.
- `pytest tests/test_rbac.py -q` → 8 passed.
- `pytest` → 407 passed.
- `flask db current` → 20260715_0066.
- `flask db heads` → 20260715_0066.

## Git

- Sprint 8.1 commit: backend foundation.
- Sprint 8.2 commit: inline clinic ultrasound UI.
- Sprint 8.3 commit: `1fa5b88` — external ultrasound request upload.
- Working tree was clean after Sprint 8.3 commit and push.

## Freeze Decision

Stage 8 is accepted as complete and safe to build on.

## Next Stage

Stage 9 — Surgery.

---
