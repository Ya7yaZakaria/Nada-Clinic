# Sprint 5.2B — Drug Database UI

## Goal
Create UI for managing the clinic drug database.

## Scope
- Drug list page.
- Drug search.
- Drug create form.
- Drug edit form.
- Drug deactivate/reactivate actions.
- Dropdowns from active medication dictionaries.
- Sidebar link.
- UI tests.

## Out of Scope
- Prescription model.
- Prescription UI.
- Prescription presets.
- Print engine.
- AI prescribing.
- Drug safety automation.

## Routes
- GET `/drugs/`
- GET/POST `/drugs/new`
- GET/POST `/drugs/<drug_uuid>/edit`
- POST `/drugs/<drug_uuid>/deactivate`
- POST `/drugs/<drug_uuid>/reactivate`

## Permissions
- `drug_settings.manage`

## Acceptance Criteria
- Doctor/Admin can access Drug Database.
- Reception receives 403.
- Authorized user can search drugs.
- Authorized user can create drugs.
- Authorized user can edit drugs.
- Authorized user can deactivate/reactivate drugs.
- Duplicate drug combination is rejected.
- Dropdowns use medication dictionaries.
- No prescription or print features added.

## Verification
Run:
```powershell
python -m pytest tests/test_drugs_ui.py -q
python -m pytest tests/test_drug_service.py -q
python -m pytest
flask db current
flask db heads
flask routes
git status
git diff --stat
Status

Pending verification.
