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
