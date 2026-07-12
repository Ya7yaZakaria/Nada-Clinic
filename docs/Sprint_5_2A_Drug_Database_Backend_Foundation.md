# Sprint 5.2A — Drug Database Backend Foundation

## Goal
Create backend foundation for the clinic drug database.

## Scope
- Drug model.
- DrugService.
- Drugs migration.
- Model tests.
- Service tests.

## Out of Scope
- Drug UI.
- Prescription model.
- Prescription UI.
- Presets.
- Print engine.
- AI prescribing.
- Drug safety automation.

## Database Table
- drugs

## Relationships
- DrugCategory
- DrugForm
- DrugRoute
- DrugSafetyStatus for pregnancy.
- DrugSafetyStatus for lactation.

## Duplicate Rule
A drug is considered duplicate when the following combination already exists:
- trade_name
- form_id
- strength

## Design Decisions
- Generic name is required.
- Trade name is required.
- Strength is required.
- Form is required.
- Category is optional.
- Route is optional.
- Pregnancy/lactation safety statuses are optional.
- Pregnancy/lactation notes are doctor-only references.
- No clinical decision support is implemented yet.
- No prescription workflow is implemented yet.

## Verification
Run:
```powershell
python -m pytest tests/test_drug_model.py -q
python -m pytest tests/test_drug_service.py -q
python -m pytest
flask db upgrade
flask db current
flask db heads
git status
git diff --stat
Status

Pending verification.
