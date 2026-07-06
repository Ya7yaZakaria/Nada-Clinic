# Stage 1 — Sprint 1.3 Settings Foundation

## Goal

Create useful clinic/system settings foundation for personalization and organization.

## Scope

- Setting model
- Settings service
- Admin settings page
- Grouped settings
- Settings seed command
- Settings tests

## Out of Scope

- Audit
- Patient CRUD
- Appointment CRUD
- Visit CRUD
- Clinical modules
- AI features
- Storing secrets or API keys in settings

## Files Created

- app/models/setting.py
- app/services/settings_service.py
- app/forms/settings_forms.py
- app/templates/admin/settings.html
- tests/test_settings.py
- migrations/versions/*_add_settings.py

## Files Modified

- app/routes/admin.py
- app/models/__init__.py
- app/forms/__init__.py
- app/templates/base.html
- app/commands.py
- README.md
- CHANGELOG.md

## Database Impact

Creates the settings table.

## Settings Groups

- clinic
- localization
- appearance
- workflow
- printing
- security
- system

## Routes

- GET /admin/settings
- POST /admin/settings

## Services

- SettingsService.get()
- SettingsService.set()
- SettingsService.get_group()
- SettingsService.get_public_settings()
- SettingsService.seed_defaults()

## Acceptance Criteria

- Settings table exists.
- Default settings exist.
- Admin can manage settings.
- Non-admin is blocked.
- Settings can be updated.
- Public settings can be read safely.
- Tests pass.
