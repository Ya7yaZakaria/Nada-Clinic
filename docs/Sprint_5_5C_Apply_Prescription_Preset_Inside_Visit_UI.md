# Sprint 5.5C — Apply Prescription Preset Inside Visit UI

## Goal
Allow Doctor/Admin users to apply an active prescription preset from inside the Visit prescription card.

## Scope
- Add apply-preset form to Visit prescription section.
- Add active preset dropdown.
- Add POST route for applying preset to Visit prescription.
- Use existing PrescriptionPresetService.apply_to_prescription.
- Create prescription automatically if the Visit has no prescription yet.
- Add editable PrescriptionItem rows from preset items.
- Add UI tests for Doctor apply, Reception blocking, empty preset error, and form visibility.

## Out of Scope
- Preset management UI.
- Print engine.
- Diagnosis-linked presets.
- AI preset suggestions.
- Automatic prescribing.
- Prescription locking.
- New database migration.

## Behavior
Applying a preset creates normal editable prescription medication lines. The doctor can edit or remove the generated lines after applying the preset. Applying a preset does not print, lock, diagnose, or change Visit status.

## Verification Commands
- python -m pytest tests/test_prescription_ui.py -q
- python -m pytest tests/test_prescription_preset_model.py tests/test_prescription_preset_service.py tests/test_prescription_presets_ui.py tests/test_prescription_ui.py -q
- python -m pytest
- flask db current
- flask db heads
