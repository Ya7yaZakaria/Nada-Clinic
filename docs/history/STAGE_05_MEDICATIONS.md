# Stage 05 Medications

Historical sprint/stage source material consolidated verbatim. It is retained for traceability and does not override current code.

## Included legacy sources

- `Sprint_5_1A_Drug_Dictionaries_Backend_Foundation.md`
- `Sprint_5_1B_Drug_Settings_UI.md`
- `Sprint_5_2A_Drug_Database_Backend_Foundation.md`
- `Sprint_5_2B_Drug_Database_UI.md`
- `Sprint_5_3A_Prescription_Backend_Foundation.md`
- `Sprint_5_4A_Prescription_UI_Inside_Visit.md`
- `Sprint_5_4B_Prescription_UI_Template_Cleanup.md`
- `Sprint_5_5A_Prescription_Presets_Backend_Foundation.md`
- `Sprint_5_5B_Prescription_Presets_Management_UI.md`
- `Sprint_5_5C_Apply_Prescription_Preset_Inside_Visit_UI.md`
- `Sprint_5_6_Prescription_Print_Engine_v1.md`
- `Sprint_5_7_Prescription_Module_Freeze_Review.md`

---

## Legacy source: `Sprint_5_1A_Drug_Dictionaries_Backend_Foundation.md`

# Sprint 5.1A — Drug Dictionaries Backend Foundation

## Goal
Create AI-ready backend foundation for editable medication dictionaries.

## Scope
This sprint adds backend-only medication dictionary foundations.

## Included
- DrugCategory model.
- DrugForm model.
- DrugRoute model.
- DrugSafetyStatus model.
- DrugDictionaryService.
- Default dictionary seed method.
- RBAC permission: drug_settings.manage.
- Admin and Doctor can manage drug settings.
- Reception is blocked.
- Alembic migration for dictionary tables.
- Model and service tests.

## Out of Scope
- Drug database model.
- Prescription model.
- Prescription UI.
- Print engine.
- Routes.
- Templates.
- AI suggestions.
- Drug safety automation.
- Reception medication access.

## Database Tables
- drug_categories
- drug_forms
- drug_routes
- drug_safety_statuses

## Permission
- drug_settings.manage

## Role Access
- Admin: allowed.
- Doctor: allowed.
- Reception: blocked.

## Design Decisions
- Medication dictionary values are structured.
- Dictionary values are editable by authorized users.
- Dictionary values are not random free text.
- Dictionary values are not permanently hardcoded in code.
- This supports future AI-ready structured medication data.
- Safety statuses are doctor-only internal references.
- No clinical decision support is implemented yet.

## Verification
- tests/test_drug_dictionaries_model.py: 3 passed.
- tests/test_drug_dictionaries_crud.py: 9 passed.
- Full test suite: 187 passed, 225 warnings.
- Migration current/head: 20260712_0051.
- No UI or prescription features added.

## Status
Complete.

---

## Legacy source: `Sprint_5_1B_Drug_Settings_UI.md`

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

---

## Legacy source: `Sprint_5_2A_Drug_Database_Backend_Foundation.md`

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

---

## Legacy source: `Sprint_5_2B_Drug_Database_UI.md`

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

---

## Legacy source: `Sprint_5_3A_Prescription_Backend_Foundation.md`

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

---

## Legacy source: `Sprint_5_4A_Prescription_UI_Inside_Visit.md`

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

---

## Legacy source: `Sprint_5_4B_Prescription_UI_Template_Cleanup.md`

# Sprint 5.4B — Prescription UI Template Cleanup

## Goal
Clean up Visit detail by extracting the Prescription section into a partial template and restoring correct Jinja block structure.

## Scope
- Create `app/templates/visits/_prescription_section.html`.
- Rewrite `app/templates/visits/detail.html` into clean structure.
- Keep existing prescription routes unchanged.
- Keep existing forms unchanged.
- Keep existing tests unchanged unless required.

## Out of Scope
- New prescription features.
- Print engine.
- Presets.
- Diagnosis.
- Database changes.
- Migration.

## Correction
Sprint 5.4A passed tests but `visits/detail.html` contained repeated prescription markup inside page blocks. This sprint restores clean template structure and moves prescription markup to a partial.

## Acceptance Criteria
- `visits/detail.html` has only title, page_title, page_subtitle, and content blocks.
- Prescription markup lives in `_prescription_section.html`.
- Visit detail renders normally.
- Prescription add/edit/remove still works.
- Reception remains blocked by RBAC.
- No database migration.
- Full test suite passes.

## Verification
```powershell
python -m pytest tests/test_prescription_ui.py -q
python -m pytest tests/test_visit_journey_link.py tests/test_visit_model.py tests/test_prescription_ui.py -q
python -m pytest
flask db current
flask db heads
git status
git diff --stat

---

## Legacy source: `Sprint_5_5A_Prescription_Presets_Backend_Foundation.md`

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

---

## Legacy source: `Sprint_5_5B_Prescription_Presets_Management_UI.md`

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

---

## Legacy source: `Sprint_5_5C_Apply_Prescription_Preset_Inside_Visit_UI.md`

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

---

## Legacy source: `Sprint_5_6_Prescription_Print_Engine_v1.md`

# Sprint 5.6 — Prescription Print Engine v1

## Goal
Add a reusable first version prescription print page.

## Scope
- Add prescription print route.
- Add standalone prescription print template.
- Add Print button inside Visit prescription card when prescription has items.
- Print patient name, MRN, date, and medication lines.
- Keep medication trade name in English.
- Keep medication patient instructions in Arabic-capable RTL layout.
- Add print-specific CSS inside the print template.
- Add UI tests for print page, print button, empty prescription redirect, and Reception blocking.

## Out of Scope
- Prescription lock-after-print.
- Prescription print history.
- Doctor identity.
- Diagnosis.
- General instructions.
- Reception print access.
- PDF generation.
- New database migration.

## Behavior
Printing opens a standalone browser print page. The page is designed for A5 browser printing and includes patient identity basics and structured medication lines only.

## Verification Commands
- python -m pytest tests/test_prescription_ui.py -q
- python -m pytest tests/test_prescription_model.py tests/test_prescription_service.py tests/test_prescription_ui.py -q
- python -m pytest
- flask db current
- flask db heads

---

## Legacy source: `Sprint_5_7_Prescription_Module_Freeze_Review.md`

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

---
