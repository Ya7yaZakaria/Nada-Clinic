# Sprint 5.3A — Prescription Backend Foundation Inside Visit

## Goal
Create backend foundation for one structured prescription per Visit.

## Scope
- Prescription model.
- PrescriptionItem model.
- PrescriptionService.
- Link prescription to Visit.
- Link prescription to Patient.
- One prescription per Visit initially.
- Structured medication items.
- Drug-linked items.
- Prescription permissions.
- Migration.
- Tests.

## Out of Scope
- Prescription UI.
- Print engine.
- Prescription presets.
- Free-text prescription as main design.
- Diagnosis printing.
- Appointment-linked prescription.
- Reception medication editing.
- AI prescribing.

## Database Impact
Creates:
- `prescriptions`
- `prescription_items`

## Migration
Revision:
- `20260713_0053_add_prescriptions`

Down revision:
- `20260712_0052`

## Rules
- Prescription belongs to Visit.
- Prescription belongs to same Patient as Visit.
- One Visit has one Prescription initially.
- Prescription does not link to Appointment.
- Prescription does not create, edit, complete, or lock Visit.
- PrescriptionItem uses active Drug from Drug Database.
- Dose, frequency, duration, and Arabic instructions are structured fields.
- Reception is blocked.

## Permissions
Added:
- `prescriptions.view`
- `prescriptions.manage`

Allowed:
- Admin
- Doctor

Blocked:
- Reception

## Acceptance Criteria
- Prescription can be created for Visit.
- Duplicate prescription for same Visit is rejected.
- Prescription patient_id is copied from Visit patient_id.
- PrescriptionItem can be added with Drug.
- Inactive Drug cannot be prescribed.
- PrescriptionItem route can default from Drug route or be overridden.
- Items can be updated and removed.
- Items are ordered by sort_order.
- Doctor has prescription permissions.
- Reception does not have prescription permissions.
- Tests pass.
- Migration head clean.

## Verification
Run:
```powershell
python -m pytest tests/test_prescription_model.py -q
python -m pytest tests/test_prescription_service.py -q
python -m pytest
flask db current
flask db heads
git status
git diff --stat
Status

Pending verification.
