# Stage 9 — Surgery Freeze Review

## Status

Frozen after cleanup.

## Scope Verified

- SurgeryCase model.
- Migration 20260715_0067.
- SurgeryService workflow.
- SurgeryAnalyticsService.
- Surgery dashboard.
- Surgery list.
- Surgery calendar.
- Surgery detail.
- Create surgery from dashboard.
- Create surgery from patient context.
- Create surgery from visit context.
- Complete surgery.
- Cancel surgery.
- Postpone surgery.
- Mark postponed surgery back as scheduled.
- Patient Timeline integration.
- Patient Surgical History / Surgery Records section.
- RBAC permissions.
- Module-level insights foundation.
- Documentation.
- Tests.

## Design Decisions Confirmed

- Surgery is an independent operational module.
- Surgery starts only when scheduled.
- No planned status exists.
- Visit plan can mention surgery without creating SurgeryCase.
- Surgery appears inside Patient Timeline like Visit but with Surgery badge/color.
- Surgery appears in Patient Workspace as surgical history/records, not as a separate Patient Workspace tab.
- Surgery insights are module-level analytics, not per-surgery insights.
- Finance is light only; full Finance remains deferred.

## Cleanup Completed

- Added dashboard Postponed / Cancelled section.
- Added mark-postponed-as-scheduled route and UI action.
- Added tests for dashboard attention section and mark scheduled workflow.
- Added freeze documentation.

## Deferred

- Surgery documents and consent.
- PatientDocument.surgery_case_id.
- Operation report printing.
- Full Finance module.
- AI/OCR.
- Anesthesia module.
- OR inventory.
- Hospital admission workflow.
- Advanced chart analytics.

## Verification Commands

```powershell
flask db current
flask db heads
python -m pytest tests/test_surgery_stage_9.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest tests/test_patient_workspace.py -q
python -m pytest
flask routes | Select-String "surgeries"
git status
git diff --stat
```

## Freeze Acceptance Criteria

- Full regression passes.
- Migration current/head is 20260715_0067.
- Surgery dashboard shows scheduled, upcoming, completed, postponed/cancelled.
- Postponed surgery can be marked scheduled.
- Invalid mark scheduled action is rejected.
- Patient timeline still shows surgery events.
- RBAC still blocks Reception.
- No migration drift.
- No backup/script files committed.
- Working tree clean after commit/push.
