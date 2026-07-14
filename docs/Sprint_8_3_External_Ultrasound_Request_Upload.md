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
