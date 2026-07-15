# Sprint 12.2 — Appearance, Night Mode, RTL Foundation

## Goal

Make Stage 12 appearance and localization settings affect the actual UI shell.

## Scope

- Apply theme settings to the base layout.
- Support light, dark, and auto theme modes.
- Apply language settings to `html lang`.
- Apply Arabic direction with `dir="rtl"`.
- Add data attributes for accent color, font size, and density preferences.
- Add CSS variables and layout rules for dark mode, accents, density, and RTL foundation.
- Add tests.

## Out of Scope

- Full Arabic translation.
- Per-user preferences.
- Logo upload.
- Print-specific redesign.
- Advanced theme builder.

## Database Impact

No migration required.

Sprint 12.2 reuses existing Stage 12.1 settings keys.

## Verification

```powershell
python -m pytest tests/test_appearance_personalization_stage_12.py -q
python -m pytest tests/test_settings_ui_stage_12.py -q
python -m pytest tests/test_settings.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
git status
git diff --stat
```
