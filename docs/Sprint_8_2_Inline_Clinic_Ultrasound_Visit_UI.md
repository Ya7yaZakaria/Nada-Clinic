# Sprint 8.2 — Inline Clinic Ultrasound Visit UI

## Goal

Allow the doctor to add, view, edit, and archive clinic ultrasound directly inside the Visit Detail page.

## Scope

- Inline Add Clinic Ultrasound form inside Visit Detail.
- Inline Edit Clinic Ultrasound form inside saved ultrasound cards.
- Clinic ultrasound cards inside Visit Detail.
- Light clinic ultrasound summary inside Patient Workspace.
- Type-specific fields for OBS, Gyne, OI/TI, and Other ultrasound.
- Store structured values in `findings_json`.
- Use `Visit.visit_date` for displayed ultrasound date.

## Out of Scope

- External ultrasound request UI.
- External ultrasound result upload UI.
- External result table.
- Separate ultrasound new/edit/detail pages.
- Canvas sketch.
- Print.
- AI/OCR.
- DICOM.
- Growth charts.

## Files Created

- `app/forms/ultrasound_forms.py`
- `app/routes/ultrasounds.py`
- `app/templates/ultrasounds/_clinic_ultrasound_form.html`
- `app/templates/ultrasounds/_clinic_ultrasound_card.html`
- `app/templates/visits/_ultrasound_section.html`
- `app/templates/patients/_ultrasound_section.html`
- `tests/test_clinic_ultrasound_ui.py`

## Files Modified

- `app/__init__.py`
- `app/routes/visits.py`
- `app/routes/patients.py`
- `app/templates/visits/detail.html`
- `app/templates/patients/detail.html`
- `README.md`
- `CHANGELOG.md`
- `MEMORY.md`

## Database Impact

No migration.

## Routes

- `POST /visits/<visit_uuid>/ultrasounds`
- `POST /ultrasounds/<ultrasound_uuid>/edit`
- `POST /ultrasounds/<ultrasound_uuid>/archive`

## Acceptance Criteria

- Doctor can add OBS clinic ultrasound inline from Visit Detail.
- Doctor can add Gyne clinic ultrasound inline from Visit Detail.
- Doctor can add OI/TI clinic ultrasound inline from Visit Detail.
- Doctor can add Other clinic ultrasound inline from Visit Detail.
- Form does not include `exam_date`.
- Form does not include `plan`.
- Ultrasound card displays date from linked Visit.
- Extra note textbox exists.
- Sketch note textbox exists.
- Ultrasound appears in Visit Detail.
- Recent clinic ultrasound appears lightly in Patient Workspace.
- Doctor/Admin can manage.
- Reception cannot manage ultrasound routes.
- Tests pass.

## Verification

```powershell
$env:FLASK_APP = "app"
$env:FLASK_ENV = "development"
$env:PYTHONPATH = (Get-Location).Path

pytest tests/test_clinic_ultrasound_ui.py -q
pytest tests/test_rbac.py -q
pytest
flask db current
flask db heads
flask routes
git status
git diff --stat
```
