# Sprint 12.3 — Clinic Profile Settings

## Goal

Add a dedicated clinic profile settings page using the existing Setting model.

## Scope

- Add clinic profile helper methods to SettingsService.
- Inject clinic profile into the global template context.
- Apply clinic name and short name to the base shell brand/title.
- Add `/settings/clinic-profile`.
- Add Clinic Profile shortcut card on the Settings dashboard.
- Add tests for access, display, updates, and shell brand integration.

## Out of Scope

- Logo upload.
- File storage for logo.
- Doctor profile records.
- Print template redesign.
- Full Arabic translation.
- Per-user preferences.

## Database Impact

No schema migration required.

Sprint 12.3 reuses existing clinic settings keys:
- clinic.name
- clinic.short_name
- clinic.phone
- clinic.whatsapp
- clinic.address
- clinic.logo_path
- clinic.default_doctor_name

## Verification

```powershell
python -m pytest tests/test_clinic_profile_settings_stage_12.py -q
python -m pytest tests/test_appearance_personalization_stage_12.py -q
python -m pytest tests/test_settings_ui_stage_12.py -q
python -m pytest tests/test_settings.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "settings"
git status
git diff --stat
```
