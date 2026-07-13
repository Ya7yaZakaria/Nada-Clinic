
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

## 2026-07-13 — Sprint 5.6 Prescription Print Engine v1
- Added standalone prescription print page from Visit.
- Added Print button when prescription has medication items.
- Print page includes patient name, MRN, date, and medication lines.
- Kept diagnosis, doctor identity, print locking, print history, PDF generation, and migration out of scope.
- Reception print access remains blocked.

## 2026-07-13 — Sprint 5.7 Prescription Module Freeze Review
- Performed Stage 5 Prescription + Printing cleanup/freeze review.
- Fixed duplicate mobile sidebar Prescription Presets link.
- Updated sidebar footer to Stage 5 Prescriptions.
- Cleaned mojibake strings in prescription UI tests.
- Added final freeze regression checks for print content and navigation.
- Confirmed no migration, print locking, print history, doctor identity, diagnosis printing, PDF generation, or AI prescribing added.
- Next action after verification: close Stage 5 and prepare Stage 6 Investigations.

## 2026-07-13 — Sprint 6.1A Investigation Dictionaries + Core Models
- Added investigation backend foundation: categories, tests, orders, order items, and results.
- Supports historical/external results without prior order.
- Supports separate ordered_visit and result_visit.
- Stores lab name, result date, value/unit/reference/text, doctor comment, abnormal flag, and attachment placeholders for Stage 7.
- Added latest result, pending ordered result, and missing test service helpers.
- Added investigation RBAC permissions for Doctor/Admin while Reception remains blocked.
- No UI, presets, print request, real upload/storage, lab integration, or AI behavior added.
- Next action: verify migration/tests, then Sprint 6.1B Investigation Orders From Visit UI.

## 2026-07-13 — Sprint 6.1B Investigation Orders From Visit UI
- Added investigation order UI from Visit.
- Added investigation blueprint/routes.
- Added order detail page and add-test workflow.
- Added patient investigations page with pending/latest sections.
- Added investigations section inside Visit detail.
- Added sidebar Investigations link.
- Kept result entry, historical result UI, presets, print request, upload/storage, AI behavior, and migration out of scope.
- Next action: verify tests/routes, then Sprint 6.2A Investigation Presets Backend or Sprint 6.3A Result Entry Backend depending on workflow priority.

## 2026-07-13 — Sprint 6.2A Investigation Presets Backend
- Added investigation preset backend foundation.
- Added InvestigationPreset and InvestigationPresetItem models.
- Added InvestigationPresetService.
- Supports applying preset to existing investigation order as normal editable order items.
- Supports missing tests from preset using latest patient results.
- Prevents duplicate preset names, duplicate tests inside a preset, and duplicate active order tests during preset apply.
- Added investigation_presets.manage permission for Doctor/Admin while Reception remains blocked.
- No preset UI, result entry UI, historical result UI, print request, upload/storage, lab integration, or AI behavior added.
- Next action: verify migration/tests, then Sprint 6.2B Investigation Presets UI.

## 2026-07-13 — Sprint 6.2B Investigation Presets UI
- Added Doctor/Admin UI for investigation preset management.
- Added investigation preset forms/routes/templates.
- Added preset list/create/edit/detail workflows.
- Added add/remove investigation test item workflows.
- Added apply preset action from investigation order detail.
- Added sidebar Investigation Presets link.
- Kept result entry UI, historical result UI, print request, upload/storage, lab integration, AI behavior, and migration out of scope.
- Next action: verify tests/routes, then Sprint 6.3A Result Entry Backend.

## 2026-07-13 — Sprint 6.3 Investigation Result Entry
- Added investigation result entry backend and UI.
- Doctors can enter result for ordered investigation item.
- Doctors can enter historical/external result from Patient or Visit context.
- Results store lab name, result date, value/text, doctor comment, abnormal flag, and attachment placeholders.
- Added result update/cancel/listing service helpers.
- Added result display in order detail and patient investigations.
- Reception remains blocked from result entry.
- Kept result review UI, print request, upload/storage, timeline integration, lab integration, and AI behavior out of scope.
- Next action: verify tests/routes, then Sprint 6.4 Result Review + Patient Workspace.

## 2026-07-13 — Sprint 6.4 Result Review + Patient Workspace
- Added investigation result review workflow.
- Doctors can review entered results, confirm abnormal flag, and store review note.
- Review stores reviewed_by_user and reviewed_at.
- Added pending result review page.
- Added Patient Workspace investigation section with pending ordered results, pending review results, latest results, and missing workup from preset.
- Added generated timeline events for investigation ordered, result entered, and result reviewed.
- Reception remains blocked from investigation result review.
- Kept AI interpretation, automatic diagnosis, upload/storage, lab integration, alerts, and print request out of scope.
- Next action: verify tests/routes, then Sprint 6.5 Investigation Print Request.

## 2026-07-13 — Sprint 6.5A Unified Print Template Backend
- Added generic PrintTemplate backend foundation for future unified print designer.
- Supports prescription and investigation_request document types.
- Stores paper size in millimeters and visual layout positions in layout_json.
- Added PrintTemplateService with default template creation, update, listing, activation, and default management.
- Added print_templates.manage permission for Doctor/Admin while Reception remains blocked.
- Added migration 20260713_0063_add_print_templates.
- Added model/service/RBAC tests.
- Existing prescription print remains temporarily until Sprint 6.5C migration.
- Kept visual designer UI, prescription migration, investigation print route, print preview, PDF generation, print history, print lock, doctor signature, logo upload, and AI behavior out of scope.
- Next action: verify migration/tests, then Sprint 6.5B Unified Visual Designer UI.

## 2026-07-13 — Sprint 6.5B Unified Visual Designer UI
- Added generic Print Templates UI.
- Added print_templates blueprint/routes.
- Added PrintTemplateForm.
- Added default template seeding action from UI.
- Added create/edit/deactivate/reactivate workflows.
- Added visual drag-and-drop designer for layout_json.
- Added sidebar Print Templates link.
- Added UI tests for access control, defaults, creation, designer save, invalid JSON, toggle, and sidebar.
- Existing prescription print remains temporarily until Sprint 6.5C migration.
- No new migration, prescription migration, investigation print route, print preview rendering, PDF generation, print history, print lock, doctor signature, logo upload, or AI behavior added.
- Next action: verify tests/routes, then Sprint 6.5C Prescription Migration to Unified Print.
