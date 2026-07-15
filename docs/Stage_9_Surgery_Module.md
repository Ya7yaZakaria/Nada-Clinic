# Stage 9 — Surgery Module

## Status

Implemented as one stage-wide script.

## Goal

Create an operational Surgery module for scheduled operations.

## Scope

- SurgeryCase model.
- SurgeryService.
- SurgeryAnalyticsService.
- Surgery forms.
- Surgery routes.
- Surgery dashboard.
- Surgery list.
- Surgery calendar grouped by date.
- Surgery detail.
- Create surgery from dashboard.
- Create surgery from patient context.
- Create surgery from visit context.
- Complete surgery.
- Cancel surgery.
- Postpone surgery.
- Patient Surgical History / Surgery Records section.
- Patient Timeline surgery events.
- Basic module-level insights.
- RBAC.
- Tests.

## Design Decisions

- Surgery starts when scheduled.
- No planned status.
- Visit plan can mention surgery without creating SurgeryCase.
- Surgery appears in Patient Timeline like Visit, with Surgery badge.
- Surgery insights are module-level analytics, not per-surgery insights.
- Finance is light only: fee, paid, payment status.
- Documents/consent are deferred.

## Deferred

- Consent upload.
- Operation report documents.
- PatientDocument.surgery_case_id.
- AI summaries.
- OCR.
- Full finance module.
- Anesthesia module.
- OR inventory.
- Admission workflow.
- Advanced charts.

## Verification

Run:

- flask db upgrade
- python -m pytest tests/test_surgery_stage_9.py -q
- python -m pytest tests/test_rbac.py -q
- python -m pytest tests/test_patient_workspace.py -q
- python -m pytest
- flask db current
- flask db heads
- flask routes
