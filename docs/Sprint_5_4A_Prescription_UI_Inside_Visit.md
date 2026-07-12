# Sprint 5.4A — Prescription UI Inside Visit

## Goal
Add structured prescription UI inside Visit detail.

## Scope
- Show Prescription section inside Visit detail.
- Add medication item from Visit detail.
- Edit medication item.
- Remove medication item.
- Drug dropdown uses active drugs only.
- Route override dropdown uses active routes.
- Doctor/Admin can manage.
- Reception blocked from medication content.
- Tests.

## Out of Scope
- Print engine.
- Presets.
- Diagnosis.
- Free-text prescription as main design.
- Appointment-linked prescriptions.
- AI prescribing.

## Routes
- POST `/visits/<visit_uuid>/prescription/items`
- GET/POST `/prescription-items/<item_uuid>/edit`
- POST `/prescription-items/<item_uuid>/remove`

## Permissions
- View section: `prescriptions.view`
- Add/edit/remove: `prescriptions.manage`

## Acceptance Criteria
- Doctor can see Prescription section in Visit detail.
- Reception cannot see Prescription section.
- Doctor can add structured medication item.
- Doctor can edit structured medication item.
- Doctor can remove medication item.
- Reception cannot add/edit/remove medication content.
- No print added.
- No presets added.
- Tests pass.

## Verification
```powershell
python -m pytest tests/test_prescription_ui.py -q
python -m pytest tests/test_prescription_model.py tests/test_prescription_service.py tests/test_prescription_ui.py -q
python -m pytest
flask db current
flask db heads
git status
git diff --stat
