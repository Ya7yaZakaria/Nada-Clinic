# Sprint 5.7 — Prescription Module Freeze Review & Cleanup

## Goal
Confirm Stage 5 Prescription + Printing foundation is stable and ready to close.

## Scope
- Review prescription routes.
- Review prescription permissions.
- Review prescription UI and print UI.
- Fix duplicate mobile sidebar Prescription Presets link.
- Update stale sidebar footer from Stage 4 to Stage 5.
- Clean mojibake strings in prescription UI tests.
- Add final freeze regression tests.
- Verify full test suite.
- Verify migration current/head.
- Confirm no unrelated features were added.

## Out of Scope
- New prescription features.
- New database migration.
- Print history.
- Print locking.
- Doctor identity in print.
- Diagnosis in print.
- Reception print access.
- PDF generation.
- AI prescribing.
- Drug interaction checking.

## Freeze Checks
- Drug dictionaries exist and are editable by authorized users.
- Drug database can grow over time.
- Doctor/Admin can manage drugs.
- Reception cannot manage drug database.
- Prescription is created inside Visit.
- Prescription is structured.
- Prescription can be printed.
- Reception cannot edit medication content.
- Presets work.
- Print engine v1 works.
- No diagnosis printed.
- No doctor identity printed.
- No safety notes printed.
- All tests pass.
- Migration head clean.
- Documentation updated.
- No unrelated features added.

## Verification Commands
- python -m pytest tests/test_prescription_ui.py -q
- python -m pytest tests/test_drug_dictionaries_model.py tests/test_drug_dictionaries_crud.py tests/test_drug_model.py tests/test_drug_service.py tests/test_drugs_ui.py tests/test_drug_settings_ui.py tests/test_prescription_model.py tests/test_prescription_service.py tests/test_prescription_ui.py tests/test_prescription_preset_model.py tests/test_prescription_preset_service.py tests/test_prescription_presets_ui.py -q
- python -m pytest
- flask db current
- flask db heads
- flask routes
- git status
- git diff --stat
