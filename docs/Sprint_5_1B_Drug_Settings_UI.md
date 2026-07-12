# Sprint 5.1B — Drug Settings UI

## Goal
Create a simple UI for managing medication dictionaries.

## Scope
- Drug Settings blueprint.
- Drug dictionary forms.
- Drug Settings index page.
- Dictionary create/edit pages.
- Seed defaults action.
- Deactivate/reactivate actions.
- Sidebar link.
- Permission protection using `drug_settings.manage`.
- UI tests.

## Out of Scope
- Drug database model.
- Prescription model.
- Prescription UI.
- Print engine.
- AI prescribing.
- Reception medication access.

## Routes
- GET `/drug-settings/`
- POST `/drug-settings/seed-defaults`
- GET/POST `/drug-settings/<dictionary_type>/new`
- GET/POST `/drug-settings/<dictionary_type>/<item_uuid>/edit`
- POST `/drug-settings/<dictionary_type>/<item_uuid>/deactivate`
- POST `/drug-settings/<dictionary_type>/<item_uuid>/reactivate`

## Permissions
- `drug_settings.manage`

## Role Rules
- Admin: allowed.
- Doctor: allowed.
- Reception: blocked.

## Acceptance Criteria
- Doctor/Admin can open Drug Settings.
- Reception receives 403.
- Authorized user can seed defaults.
- Authorized user can create dictionary items.
- Authorized user can edit dictionary items.
- Authorized user can deactivate/reactivate dictionary items.
- No Drug model added.
- No Prescription model added.
- Tests pass.
- Migration head remains clean.

## Verification
Run:
```powershell
python -m pytest tests/test_drug_settings_ui.py -q
python -m pytest tests/test_drug_dictionaries_model.py -q
python -m pytest tests/test_drug_dictionaries_crud.py -q
python -m pytest
flask db current
flask db heads
flask routes
git status
git diff --stat
