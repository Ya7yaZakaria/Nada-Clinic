# Sprint 12.4 — Workflow Defaults

## Goal

Make the existing workflow default landing setting operational.

## Scope

- Resolve `workflow.default_landing_page` to safe route endpoints.
- Redirect successful login to the configured default landing page.
- Keep a safe dashboard fallback for invalid targets.
- Show workflow default status in Settings dashboard.
- Add focused tests.

## Out of Scope

- Dashboard redesign.
- Admin Home redesign.
- Per-user landing preferences.
- New workflow database tables.
- Notifications.
- Follow-up engine implementation.

## Database Impact

No schema migration required.

Sprint 12.4 reuses existing settings:
- workflow.default_landing_page
- workflow.enable_today_clinic
- workflow.enable_patient_workspace
- workflow.enable_followup_tracker

## Verification

```powershell
python -m pytest tests/test_workflow_defaults_stage_12.py -q
python -m pytest tests/test_auth.py -q
python -m pytest tests/test_settings_ui_stage_12.py -q
python -m pytest tests/test_settings.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "settings|auth"
git status
git diff --stat
```
