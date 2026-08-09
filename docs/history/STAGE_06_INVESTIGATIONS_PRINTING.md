# Stage 06 Investigations Printing

Historical sprint/stage source material consolidated verbatim. It is retained for traceability and does not override current code.

## Included legacy sources

- `Sprint_6_1A_Investigation_Dictionaries_Core_Models.md`
- `Sprint_6_1B_Investigation_Orders_From_Visit_UI.md`
- `Sprint_6_2A_Investigation_Presets_Backend.md`
- `Sprint_6_2B_Investigation_Presets_UI.md`
- `Sprint_6_3_Result_Entry.md`
- `Sprint_6_4_Result_Review_Patient_Workspace.md`
- `Sprint_6_5A_Unified_Print_Template_Backend.md`
- `Sprint_6_5B_Unified_Visual_Designer_UI.md`
- `Sprint_6_5C_Prescription_Migration_Unified_Print.md`
- `Sprint_6_5D_Investigation_Print_Unified_Designer.md`
- `Sprint_6_5E_Print_Module_Freeze_Review.md`
- `Stage_6_Investigation_Module_Freeze_Review.md`

---

## Legacy source: `Sprint_6_1A_Investigation_Dictionaries_Core_Models.md`

# Sprint 6.1A — Investigation Dictionaries + Core Models

## Goal
Create the backend foundation for the Investigations Module.

## Scope
- Investigation categories.
- Investigation tests.
- Investigation orders.
- Investigation order items.
- Investigation results.
- Result without prior order.
- Separate ordered visit and result visit.
- Lab name and result date.
- Result value/unit/reference range/text.
- Doctor comment.
- Abnormal flag.
- Attachment placeholder for Stage 7.
- Latest result service.
- Pending ordered result service.
- Missing tests from required list foundation.
- Investigation RBAC permissions.
- Migration.
- Tests.

## Out of Scope
- UI.
- Presets.
- Printing.
- Real file upload/storage.
- AI extraction.
- Lab integration.
- Patient Workspace integration.
- Timeline integration.

## Design Decisions
- Historical/external results can be recorded without prior order.
- Ordered visit and result visit are separate.
- CBC and complex investigations start as one test with text/report fields.
- Upload/storage is prepared only with placeholders.
- AI-ready data exists, but no AI behavior is added.

## Verification Commands
- flask db upgrade
- flask db current
- flask db heads
- python -m pytest tests/test_investigation_model.py -q
- python -m pytest tests/test_investigation_dictionary_service.py -q
- python -m pytest tests/test_investigation_service.py -q
- python -m pytest
- git status
- git diff --stat

---

## Legacy source: `Sprint_6_1B_Investigation_Orders_From_Visit_UI.md`

# Sprint 6.1B — Investigation Orders From Visit UI

## Goal
Allow doctors to create investigation orders from a Visit and add individual investigation tests.

## Scope
- Investigation forms.
- Investigation blueprint/routes.
- Investigation order creation from Visit.
- Investigation order detail page.
- Add test to order workflow.
- Cancel order item workflow.
- Patient investigations page.
- Visit detail investigations section.
- Sidebar Investigations link.
- UI tests.
- Documentation.

## Out of Scope
- Result entry UI.
- Historical result UI.
- Presets.
- Print request.
- Upload/storage.
- AI behavior.
- Timeline integration.
- New migration.

## Routes
- GET /investigations/
- GET /investigations/patients/<patient_uuid>
- GET, POST /investigations/visits/<visit_uuid>/new
- GET /investigations/orders/<order_uuid>
- POST /investigations/orders/<order_uuid>/items
- POST /investigations/items/<item_uuid>/cancel

## Acceptance Criteria
- Doctor can see investigations section inside Visit.
- Doctor can create an investigation order from Visit.
- Doctor can add an individual test to an order.
- Pending tests appear in Visit detail.
- Patient investigations page shows pending/latest sections.
- Reception cannot create investigation orders.
- No result entry, presets, print, upload, AI, or migration added.

## Verification Commands
- python -m pytest tests/test_investigation_ui.py -q
- python -m pytest tests/test_investigation_model.py tests/test_investigation_dictionary_service.py tests/test_investigation_service.py tests/test_investigation_ui.py -q
- python -m pytest
- flask db current
- flask db heads
- flask routes
- git status
- git diff --stat

---

## Legacy source: `Sprint_6_2A_Investigation_Presets_Backend.md`

# Sprint 6.2A — Investigation Presets Backend

## Goal
Create backend support for reusable investigation panels/workups.

## Scope
- Investigation preset model.
- Investigation preset item model.
- Investigation preset service.
- Apply preset to investigation order.
- Missing tests from preset using latest patient results.
- RBAC permission for investigation preset management.
- Migration.
- Model and service tests.

## Out of Scope
- Preset UI.
- Result entry UI.
- Historical result UI.
- Print request.
- Upload/storage.
- AI behavior.
- Patient Workspace UI changes.
- Timeline integration.

## Models
- InvestigationPreset
- InvestigationPresetItem

## Service
InvestigationPresetService supports:
- create/update preset
- deactivate/reactivate preset
- add/remove/list preset items
- list active/all presets
- apply preset to order
- missing tests for patient

## Rules
- Preset name is required and unique.
- Inactive tests cannot be added.
- Duplicate tests inside same preset are rejected.
- Applying a preset creates normal InvestigationOrderItem rows.
- Applying a preset skips tests already active in the order.
- Applying inactive or empty preset fails.
- Applying to cancelled order fails.
- Missing tests use latest non-cancelled results.

## Verification Commands
- flask db upgrade
- flask db current
- flask db heads
- python -m pytest tests/test_investigation_preset_model.py -q
- python -m pytest tests/test_investigation_preset_service.py -q
- python -m pytest
- git status
- git diff --stat

---

## Legacy source: `Sprint_6_2B_Investigation_Presets_UI.md`

# Sprint 6.2B — Investigation Presets UI

## Goal
Allow doctors to manage investigation presets and apply them to investigation orders.

## Scope
- Investigation preset forms.
- Investigation preset blueprint/routes.
- Preset list/create/edit/detail UI.
- Add/remove preset tests.
- Apply preset to investigation order.
- Sidebar Investigation Presets link.
- UI tests.
- Documentation.

## Out of Scope
- Result entry.
- Historical result UI.
- Print request.
- Upload/storage.
- AI behavior.
- Advanced missing-workup dashboard.
- New migration.

## Routes
- GET /investigation-presets/
- GET, POST /investigation-presets/new
- GET /investigation-presets/<preset_uuid>
- GET, POST /investigation-presets/<preset_uuid>/edit
- POST /investigation-presets/<preset_uuid>/deactivate
- POST /investigation-presets/<preset_uuid>/reactivate
- POST /investigation-presets/<preset_uuid>/items
- POST /investigation-presets/items/<item_uuid>/remove
- POST /investigations/orders/<order_uuid>/apply-preset

## Acceptance Criteria
- Doctor can create investigation preset.
- Doctor can add tests to preset.
- Doctor can remove tests from preset.
- Doctor can apply preset to order.
- Applied tests appear as normal editable order items.
- Reception cannot manage presets.
- Full tests pass.
- No migration drift.

## Verification Commands
- python -m pytest tests/test_investigation_presets_ui.py -q
- python -m pytest tests/test_investigation_preset_model.py tests/test_investigation_preset_service.py tests/test_investigation_presets_ui.py -q
- python -m pytest
- flask db current
- flask db heads
- flask routes
- git status
- git diff --stat

---

## Legacy source: `Sprint_6_3_Result_Entry.md`

# Sprint 6.3 — Investigation Result Entry

## Goal
Allow doctors to enter investigation results for ordered items and historical/external results without prior order.

## Scope
- Hardened result service validation.
- Ordered result entry backend.
- Historical result entry backend.
- Result update/cancel service helpers.
- Patient/visit/order-item result listing helpers.
- Entered/unreviewed result listing helper.
- Result entry forms.
- Ordered result entry route/page.
- Historical result entry from Patient.
- Historical result entry from Visit.
- Result display in order detail and patient investigations.
- Tests.

## Out of Scope
- Result review UI.
- Actual file upload/storage.
- Print request.
- AI extraction.
- AI interpretation.
- Timeline integration.
- New migration.

## Acceptance Criteria
- Doctor can enter result for ordered investigation item.
- Doctor can enter historical result without order.
- Result stores lab name, date, value/text, doctor comment, abnormal flag, and attachment placeholders.
- Ordered item status updates after result entry.
- Order status updates after result entry.
- Result appears in patient investigations.
- Reception cannot enter result.
- Full tests pass.
- No migration drift.

---

## Legacy source: `Sprint_6_4_Result_Review_Patient_Workspace.md`

# Sprint 6.4 — Result Review + Patient Workspace

## Goal
Allow doctors to review entered investigation results and surface investigation data inside Patient Workspace.

## Scope
- Result review form.
- Pending result review page.
- Review POST workflow.
- Reviewed status.
- Reviewed by doctor.
- Reviewed at timestamp.
- Review note.
- Abnormal flag confirmation.
- Patient Workspace pending ordered results.
- Patient Workspace pending review results.
- Patient Workspace latest results.
- Patient Workspace missing workup from preset.
- Generated timeline investigation events.
- Service/UI tests.

## Out of Scope
- AI interpretation.
- Automatic diagnosis.
- Patient notifications.
- Advanced alerts.
- Lab integration.
- Complex reference ranges.
- Real upload/storage.
- Print request.

## Routes
- GET /investigations/pending
- POST /investigations/results/<result_uuid>/review
- GET /patients/<patient_uuid>?preset_id=<preset_id>

## Acceptance Criteria
- Doctor can review result.
- Review stores reviewed_by_user, reviewed_at, review_note.
- Abnormal flag can be confirmed.
- Pending results disappear after review.
- Latest results appear in Patient Workspace.
- Missing workup can be shown from preset.
- Timeline includes investigation result and reviewed events.
- Reception cannot review.
- Full test suite passes.
- No migration drift.

---

## Legacy source: `Sprint_6_5A_Unified_Print_Template_Backend.md`

# Sprint 6.5A — Unified Print Template Backend

## Goal
Create a reusable backend foundation for visual print templates that can later serve both prescription printing and investigation request printing.

## Scope
- Generic PrintTemplate model.
- Generic PrintTemplateService.
- Document types:
  - prescription
  - investigation_request
- JSON-based layout storage.
- Paper size storage in millimeters.
- Default template support.
- Active/inactive template support.
- One default template per document type enforced by service.
- RBAC permission for print template management.
- Migration.
- Model/service/RBAC tests.

## Out of Scope
- Visual drag-and-drop designer UI.
- Prescription route migration.
- Investigation print route.
- Old prescription print deletion.
- Print preview page.
- PDF generation.
- Print history.
- Print locking.
- Doctor signature.
- Logo upload.
- Multi-page printing.
- AI behavior.

## Database Impact
Creates table:

- print_templates

Fields:
- id
- uuid
- name
- document_type
- paper_width_mm
- paper_height_mm
- layout_json
- is_default
- is_active
- created_by_user_id
- updated_by_user_id
- created_at
- updated_at

## Permissions
Adds:
- print_templates.manage

Doctor/Admin can manage print templates.
Reception remains blocked.

## Acceptance Criteria
- PrintTemplate table exists.
- Prescription and investigation_request document types are supported.
- Default templates can be created idempotently.
- Layout JSON can be stored and updated.
- Same template name is allowed across different document types.
- Duplicate names are blocked within the same document type.
- Only one default active template is kept per document type by service.
- Doctor/Admin receive print_templates.manage.
- Reception does not receive print_templates.manage.
- Existing prescription print remains temporarily until Sprint 6.5C migration.
- Migration applies cleanly.
- Full suite passes.

---

## Legacy source: `Sprint_6_5B_Unified_Visual_Designer_UI.md`

# Sprint 6.5B — Unified Visual Designer UI

## Goal
Add a generic visual designer UI for PrintTemplate records so doctors/admins can create, select, drag, reposition, and save reusable layouts before prescription and investigation printing are migrated to the unified engine.

## Scope
- New print_templates blueprint.
- Print template list page.
- Seed default templates action.
- Create/edit template metadata.
- Deactivate/reactivate templates.
- Generic visual designer page.
- Drag-and-drop visible elements on a paper canvas.
- Save layout_json back to PrintTemplate.
- Sidebar link.
- UI tests.

## Out of Scope
- Prescription route migration.
- Investigation print route.
- Old prescription print deletion.
- Real patient/order data print preview.
- PDF generation.
- Print history.
- Print locking.
- Doctor signature.
- Logo upload.
- Multi-page printing.
- AI behavior.

## Routes
- GET  /print/templates/
- POST /print/templates/seed-defaults
- GET  /print/templates/new
- POST /print/templates/new
- GET  /print/templates/<template_uuid>/edit
- POST /print/templates/<template_uuid>/edit
- GET  /print/templates/<template_uuid>/designer
- POST /print/templates/<template_uuid>/layout
- POST /print/templates/<template_uuid>/deactivate
- POST /print/templates/<template_uuid>/reactivate

## Permissions
Uses:
- print_templates.manage

Doctor/Admin can manage print templates.
Reception remains blocked.

## Database Impact
No new migration.

## Acceptance Criteria
- Doctor/Admin can open print templates index.
- Reception cannot open print templates index.
- Doctor/Admin can seed default templates.
- Doctor/Admin can create/edit/deactivate/reactivate templates.
- Doctor/Admin can open visual designer.
- Designer shows paper canvas and layout elements.
- Layout JSON can be saved.
- Invalid layout JSON is rejected safely.
- Sidebar shows Print Templates link.
- Existing prescription print route remains unchanged until Sprint 6.5C.
- Full suite passes.

---

## Legacy source: `Sprint_6_5C_Prescription_Migration_Unified_Print.md`

# Sprint 6.5C — Prescription Migration to Unified Print

## Goal
Migrate prescription printing from the legacy standalone Visit print page to the unified PrintTemplate-based print engine.

## Scope
- Add unified prescription print preview route.
- Add prescription designer redirect route.
- Render prescription content using PrintTemplate.layout_json.
- Use default prescription print template automatically.
- Allow optional template_uuid query parameter for custom prescription layouts.
- Update Visit prescription Print button to unified route.
- Remove old visits.print_prescription route.
- Remove old visits/prescription_print.html template.
- Update prescription print tests.
- Add dedicated unified prescription print tests.
- Update documentation.

## Out of Scope
- Investigation print route.
- PDF generation.
- Print history.
- Print locking.
- Doctor signature.
- Logo upload.
- Multi-page printing.
- AI behavior.

## Routes Added
- GET /print/prescriptions/<visit_uuid>/designer
- GET /print/prescriptions/<visit_uuid>/preview

## Routes Removed
- GET /visits/<visit_uuid>/prescription/print

## Templates Added
- app/templates/print_templates/prescription_preview.html

## Templates Removed
- app/templates/visits/prescription_print.html

## Database Impact
No new migration.

## Permissions
Uses:
- prescriptions.view for unified prescription print preview.

Reception remains blocked because Reception does not have prescription view permission.

## Acceptance Criteria
- Doctor can open unified prescription print preview.
- Preview uses PrintTemplate layout_json.
- Preview includes patient name, MRN, date, and medication lines.
- Preview excludes diagnosis, doctor identity, safety notes, print lock, and history.
- Visit Print button points to /print/prescriptions/.
- Legacy /visits/<visit_uuid>/prescription/print route is removed.
- Old visits/prescription_print.html is removed.
- Reception cannot open unified prescription print preview.
- No new migration is added.
- Full suite passes.

---

## Legacy source: `Sprint_6_5D_Investigation_Print_Unified_Designer.md`

# Sprint 6.5D — Investigation Print Using Unified Designer

## Goal
Add investigation request printing using the unified PrintTemplate-based print engine.

## Scope
- Add unified investigation request preview route.
- Add investigation request designer redirect route.
- Render investigation order content using PrintTemplate.layout_json.
- Use default investigation request print template automatically.
- Allow optional template_uuid query parameter for custom investigation request layouts.
- Add Print request button to investigation order detail.
- Add dedicated unified investigation print tests.
- Update documentation.

## Out of Scope
- PDF generation.
- Print history.
- Print locking.
- Doctor signature.
- Logo upload.
- Result report printing.
- Lab integration.
- AI behavior.
- New database migration.

## Routes Added
- GET /print/investigations/<order_uuid>/designer
- GET /print/investigations/<order_uuid>/preview

## Templates Added
- app/templates/print_templates/investigation_request_preview.html

## Database Impact
No new migration.

## Permissions
Uses:
- investigations.view for unified investigation request print preview.

Reception remains blocked because Reception does not have investigations view permission.

## Acceptance Criteria
- Doctor can open unified investigation request print preview.
- Preview uses PrintTemplate.layout_json.
- Preview includes patient name, MRN, date, instruction, and investigation lines.
- Preview excludes result report printing.
- Investigation order detail shows Print request button when the order has items.
- Empty order redirects with warning.
- Reception cannot open unified investigation request print preview.
- No new migration is added.
- Full suite passes.

---

## Legacy source: `Sprint_6_5E_Print_Module_Freeze_Review.md`

# Sprint 6.5E — Print Module Freeze Review

## Goal
Freeze-review the unified print module after prescription and investigation request printing were migrated to the PrintTemplate-based print engine.

## Scope Reviewed
- PrintTemplate backend model/service.
- PrintTemplate management UI.
- Visual layout designer.
- Prescription unified print preview.
- Investigation request unified print preview.
- PrintTemplate default creation.
- Print routes.
- RBAC.
- Tests.
- Documentation.
- Migration state.

## Confirmed Features
- Generic PrintTemplate model supports prescription and investigation_request document types.
- PrintTemplateService creates and manages default layouts.
- Print Templates UI supports list/create/edit/deactivate/reactivate.
- Visual designer saves layout_json.
- Prescription printing uses /print/prescriptions/<visit_uuid>/preview.
- Investigation request printing uses /print/investigations/<order_uuid>/preview.
- Prescription Visit Print button points to the unified print route.
- Investigation order detail exposes Print request when items exist.
- Legacy prescription print route/template removed.
- Reception remains blocked from prescription and investigation print workflows.

## Out of Scope Confirmed
- No PDF generation.
- No print history.
- No print lock.
- No doctor signature.
- No logo upload.
- No result report printing.
- No lab integration.
- No AI behavior.
- No new migration after 20260713_0063.

## Verification Commands
- python -m pytest tests/test_print_template_model.py -q
- python -m pytest tests/test_print_template_service.py -q
- python -m pytest tests/test_print_template_ui.py -q
- python -m pytest tests/test_prescription_unified_print.py -q
- python -m pytest tests/test_investigation_unified_print.py -q
- python -m pytest tests/test_prescription_ui.py -q
- python -m pytest tests/test_investigation_ui.py -q
- python -m pytest tests/test_rbac.py -q
- python -m pytest
- flask db current
- flask db heads
- flask routes

## Acceptance Criteria
- Full suite passes.
- Migration current/head remains 20260713_0063.
- Unified prescription print routes exist.
- Unified investigation print routes exist.
- Legacy prescription print template remains removed.
- PrintTemplate docs exist.
- Working tree contains only freeze-review documentation updates after verification.

## Freeze Decision
Sprint 6.5 Print Module can be frozen after successful verification output is reviewed.

---

## Legacy source: `Stage_6_Investigation_Module_Freeze_Review.md`

# Stage 6 — Investigation Module Freeze Review

## Goal
Freeze-review Stage 6 Investigations after completing investigation dictionaries, orders, presets, result entry, historical results, result review, patient workspace investigation display, timeline events, and unified investigation request printing.

## Scope Reviewed
- Investigation dictionaries.
- Investigation tests.
- Investigation orders from Visit.
- Investigation order detail.
- Add/cancel investigation order items.
- Investigation presets backend and UI.
- Apply preset to investigation order.
- Ordered result entry.
- Enter pending ordered results from the current Visit while preserving the original ordered Visit.
- Historical/external result entry from Patient and Visit contexts.
- Result review workflow.
- Pending result review queue.
- Patient Workspace investigation section.
- Timeline events for investigation ordered, result entered, and result reviewed.
- Unified investigation request print preview.
- RBAC and Reception blocking.
- Stage 5 prescription regression after unified print migration.

## Stage 5 Regression Reviewed
- Drug dictionaries.
- Drug database.
- Prescription model/service/UI.
- Prescription presets.
- Apply prescription preset inside Visit.
- Unified prescription print preview.
- Legacy prescription print route/template removal.
- Reception blocking.

## Confirmed Architecture
- Patient remains root entity.
- Visit remains the clinical encounter.
- InvestigationOrder belongs to Patient and may link to ordered_visit and Journey.
- InvestigationResult supports ordered and historical/external workflows.
- Result entry and result review are separate workflows.
- Investigation request printing uses the unified PrintTemplate engine.
- Result report printing remains out of scope until Documents/Storage.

## Cleanup Performed
- Ordered result current Visit context fix: results can now be entered from a later Visit and stored with `result_visit_id` pointing to the current Visit while `ordered_visit_id` remains the original ordering Visit.
- Cleaned the Visit investigation test choice label separator from mojibake/question mark to a normal dash.

## Out of Scope Confirmed
- No real file upload/storage.
- No document repository.
- No PDF generation.
- No result report printing.
- No lab integration.
- No AI interpretation.
- No automatic diagnosis.
- No alerts/notifications.
- No billing/finance.
- No new database migration in this freeze sprint.

## Verification Commands
- Stage 5 prescription regression tests.
- Stage 6 investigation model/service/UI/result/review/print tests.
- Shared patient workspace, visit, timeline, RBAC tests.
- Full test suite.
- flask db current.
- flask db heads.
- flask routes.
- Static route/template checks.

## Acceptance Criteria
- Full suite passes.
- Migration current/head remains 20260713_0063.
- Prescription unified print remains working.
- Investigation unified print remains working.
- Investigation orders, presets, results, reviews, patient workspace, and timeline tests pass.
- Reception remains blocked by RBAC.
- Legacy prescription print template remains removed.
- Only cleanup/doc changes remain pending after verification.

## Freeze Decision
Stage 6 Investigation Module can be frozen after successful verification output is reviewed and committed.

## Recommended Next Stage
Stage 7 — Documents & Storage.

Rationale:
- Investigation results already contain attachment placeholders.
- Stage 7 should implement real file/document storage before result report printing, ultrasound images, surgery documents, and future AI document summarization.

---
