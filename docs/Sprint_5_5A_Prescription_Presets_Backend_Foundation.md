# Sprint 5.5A — Prescription Presets Backend Foundation

## Goal
Add backend support for reusable global prescription presets.

## Scope
- Add PrescriptionPreset model.
- Add PrescriptionPresetItem model.
- Add PrescriptionPresetService.
- Add migration for preset tables.
- Add permission `prescription_presets.manage`.
- Allow Doctor/Admin to manage presets.
- Keep Reception blocked.
- Add model and service tests.

## Out of Scope
- Preset UI.
- Apply preset button inside Visit UI.
- Print engine.
- Diagnosis-linked presets.
- AI preset suggestions.
- Automatic prescribing.

## Behavior
Prescription presets are global reusable medication sets.

Applying a preset creates normal editable PrescriptionItem rows inside a prescription.

Presets do not:
- Print
- Lock
- Diagnose
- Modify Visit status
- Auto-prescribe without explicit service call

## Verification Commands
- python -m pytest tests/test_prescription_preset_model.py -q
- python -m pytest tests/test_prescription_preset_service.py -q
- python -m pytest tests/test_prescription_model.py tests/test_prescription_service.py tests/test_prescription_preset_model.py tests/test_prescription_preset_service.py -q
- python -m pytest
- flask db current
- flask db heads

## Verification Result
- Preset model tests: 4 passed.
- Preset service tests: 8 passed.
- Combined prescription/preset tests: 26 passed.
- Full suite: 249 passed.
- Migration current/head: 20260713_0054.
