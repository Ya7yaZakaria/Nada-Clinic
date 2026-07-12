
## 2026-07-12 — Stage 4 Appointment & Today’s Clinic Frozen
- Completed Sprint 4.6 Freeze Review.
- Stage 4 is frozen and accepted.
- Verified appointment model, patient relationship, fixed appointment types, status workflow, booking, calendar, emergency unscheduled, arrival/waiting, cancel/reschedule, end-of-day no-show conversion, Today’s Clinic, and Previous Days Clinic.
- Confirmed Appointment does not create Visit automatically.
- Confirmed Doctor opens Patient Workspace and starts Visit manually.
- Confirmed Procedure is deferred as Visit add-on.
- Confirmed no billing implementation yet.
- Verification: 175 passed, 225 warnings, migration head ecf98d78d1b4, working tree clean.
- Last accepted commit before freeze docs: cb7b70c.
- Next stage candidate: Stage 5 Prescription / Printing.

## 2026-07-12 — Sprint 5.1A Drug Dictionaries Backend Foundation Completed
- Added AI-ready medication dictionary backend foundation.
- Added DrugCategory, DrugForm, DrugRoute, and DrugSafetyStatus models.
- Added DrugDictionaryService with default seed lists and active dictionary helpers.
- Added `drug_settings.manage` permission.
- Admin and Doctor can manage drug settings.
- Reception remains blocked from treatment-related settings.
- Added migration `20260712_0051_add_drug_dictionaries`.
- Added model/service tests for drug dictionaries.
- Verified: 187 passed, 225 warnings, migration head 20260712_0051.
- No Drug model, Prescription model, UI, routes, or print engine added yet.
- Next action: Sprint 5.1B Drug Settings UI or Sprint 5.2 Drug Database Foundation.

## 2026-07-12 — Sprint 5.1B Drug Settings UI Completed
- Added Drug Settings UI for medication dictionaries.
- Added forms for dictionary items and safety statuses.
- Added Drug Settings routes.
- Added Drug Settings templates.
- Added sidebar link.
- Added seed defaults UI action.
- Added create/edit/deactivate/reactivate workflows.
- Confirmed Doctor/Admin can manage medication dictionaries.
- Confirmed Reception is blocked.
- Fixed Jinja `dictionary.items` collision by using `records`.
- Verified: 195 passed, 225 warnings, migration head 20260712_0051.
- No Drug model, Prescription model, or print engine added yet.
- Next action: Sprint 5.2 Drug Database Foundation.

## 2026-07-12 — Sprint 5.2A Drug Database Backend Foundation Completed
- Added Drug model.
- Added DrugService.
- Added migration `20260712_0052_add_drugs`.
- Drug links to category, form, route, pregnancy safety status, and lactation safety status.
- Added duplicate prevention for trade name + form + strength.
- Added active drug listing and search by trade/generic/strength.
- Updated old dictionary test because Drug model now exists.
- Verified: 210 passed, 225 warnings, migration head 20260712_0052.
- No Drug UI, Prescription model, Prescription UI, presets, or print engine added yet.
- Next action: Sprint 5.2B Drug Database UI.

## 2026-07-13 — Sprint 5.2B Drug Database UI Completed
- Added Drug Database UI.
- Added DrugForm.
- Added drugs blueprint and routes.
- Added drug list/search/create/edit/deactivate/reactivate templates.
- Added sidebar link.
- Added UI tests for drug database workflows.
- Confirmed Doctor/Admin can manage drugs.
- Confirmed Reception is blocked.
- Confirmed full suite: 217 passed.
- Cleaned appointment timestamp warnings by replacing deprecated datetime.utcnow defaults with timezone-aware UTC callables.
- Migration remains 20260712_0052 head.
- No Prescription model, Prescription UI, presets, or print engine added yet.
- Next action: Sprint 5.3A Prescription Backend Foundation inside Visit.

## 2026-07-13 — Sprint 5.3A Prescription Backend Foundation Completed
- Added Prescription model.
- Added PrescriptionItem model.
- Added PrescriptionService.
- Added prescriptions.view and prescriptions.manage permissions.
- Added migration 20260713_0053_add_prescriptions.
- Confirmed Prescription belongs to Visit, not Appointment.
- Confirmed one Prescription per Visit initially.
- Confirmed PrescriptionItem uses active Drug from Drug Database.
- Confirmed structured dose/frequency/duration/instructions_ar fields.
- Confirmed Reception is blocked from prescription permissions.
- Confirmed full suite after migration: 231 passed.
- Migration current/head: 20260713_0053.
- No Prescription UI, presets, or print engine added yet.
- Next action: Sprint 5.4A Prescription UI Inside Visit.

## 2026-07-13 — Sprint 5.4A Prescription UI Inside Visit Completed
- Added Prescription UI section inside Visit detail.
- Added PrescriptionItemForm.
- Added add/edit/remove medication item routes.
- Added medication item edit template.
- Added tests/test_prescription_ui.py.
- Confirmed Doctor can manage structured prescription items from Visit detail.
- Confirmed Reception is blocked from Visit detail and prescription workflows under current RBAC.
- Confirmed active drugs are used for medication selection.
- Confirmed no print engine, presets, diagnosis, or new migration added.
- Verification: 237 passed.
- Migration current/head: 20260713_0053.
- Next action: Sprint 5.5 Prescription Presets, or optional 5.4B UI cleanup/partial extraction.

2026-07-13 — Sprint 5.5A Prescription Presets Backend Foundation
Added PrescriptionPreset and PrescriptionPresetItem backend design.
Added PrescriptionPresetService for preset CRUD, item management, and applying presets to prescriptions.
Added prescription_presets.manage permission for Doctor/Admin.
Kept Reception blocked from preset management.
Added migration 20260713_0054_add_prescription_presets.
Added model/service tests.
No UI, print, diagnosis-linked presets, or AI prescribing added.

## 2026-07-13 — Sprint 5.5B Prescription Presets Management UI
- Added Doctor/Admin UI for prescription preset management.
- Added preset list/create/edit/toggle workflows.
- Added preset detail page with medication item add/edit/remove.
- Added sidebar link for Prescription Presets.
- Added UI tests for preset workflows and Reception blocking.
- No apply-to-visit UI, print engine, migration, diagnosis-linked presets, or AI prescribing added.

## 2026-07-13 — Sprint 5.5C Apply Prescription Preset Inside Visit UI
- Added apply-preset control inside Visit prescription section.
- Added active preset dropdown and POST apply route.
- Applying a preset creates editable PrescriptionItem rows.
- Prescription is created automatically if missing.
- Added UI tests for apply preset flow, Reception blocking, and empty preset error.
- No migration, print engine, AI prescribing, diagnosis-linked suggestions, or locking added.
