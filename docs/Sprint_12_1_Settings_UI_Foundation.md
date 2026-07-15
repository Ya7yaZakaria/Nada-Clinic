# Sprint 12.1 — Settings UI Foundation

## Goal

Create a Settings dashboard and grouped settings editor using the existing `Setting` model and `SettingsService`.

## Scope

- Add `/settings/`.
- Add settings group pages.
- Add single setting edit page.
- Add seed defaults action.
- Add choice validation for key personalization settings.
- Add Stage 12 personalization keys.
- Add sidebar link.
- Add tests.
- Add documentation.

## Out of Scope

- Full dark mode CSS.
- Full Arabic translation.
- Per-user preferences.
- Logo upload.
- Notification settings.
- Permission editor.

## Database Impact

No schema migration expected.

New default setting keys are seeded through `SettingsService.DEFAULT_SETTINGS`.

## Routes

- `GET /settings/`
- `GET /settings/<group>`
- `GET, POST /settings/edit/<setting_key>`
- `POST /settings/seed-defaults`

## Permissions

- `settings.view`
- `settings.manage`

Existing RBAC is preserved.

## Verification

```powershell
python -m pytest tests/test_settings.py -q
python -m pytest tests/test_settings_ui_stage_12.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "settings"
git status
git diff --stat
```
