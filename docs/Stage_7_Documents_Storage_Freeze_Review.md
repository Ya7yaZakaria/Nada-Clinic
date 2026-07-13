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
