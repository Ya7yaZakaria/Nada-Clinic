# Sprint 5.5B — Prescription Presets Management UI

## Goal
Add UI management for reusable global prescription presets.

## Scope
- Preset list page.
- Create preset page.
- Edit preset page.
- Activate/deactivate preset.
- Preset detail page.
- Add medication item to preset.
- Edit preset medication item.
- Remove preset medication item.
- Doctor/Admin access through `prescription_presets.manage`.
- Reception blocked.
- Sidebar link.

## Out of Scope
- Apply preset to Visit prescription UI.
- Print engine.
- Diagnosis-linked presets.
- AI preset suggestions.
- Automatic prescribing.
- New database migration.

## Behavior
Prescription presets are managed as global reusable structured medication sets. Preset medications are structured using existing Drug database records.

## Verification Commands
- python -m pytest tests/test_prescription_presets_ui.py -q
- python -m pytest tests/test_prescription_preset_model.py tests/test_prescription_preset_service.py tests/test_prescription_presets_ui.py -q
- python -m pytest
- flask db current
- flask db heads
