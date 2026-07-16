# Changelog

## 2026-07-07 — Stage 3 / Sprint 3.4 Timeline Foundation

### Added

- Generated TimelineService.
- Patient Workspace timeline section.
- Journey started timeline events.
- Journey closed timeline events.
- Visit timeline events.
- Visit completed timeline events.
- Visit reopened timeline events.
- Unassigned Visit marker.
- Timeline tests.
- Sprint 3.4 documentation.

### Not Added Yet

- Timeline table.
- Manual timeline events.
- Timeline filters.
- Prescription events.
- Investigation events.
- Ultrasound events.
- Appointment events.
- Surgery events.
# Changelog

## 2026-07-07 — Stage 3 / Sprint 3.3 Link Visit to Journey

### Added

- Nullable `journey_id` on visits.
- Visit to Journey relationship.
- Visit forms.
- Visit routes.
- Visit templates.
- Optional Journey selection during Visit creation/editing.
- Assign/remove Journey link.
- Same-patient Journey validation.
- Standalone Visit warning.
- Active Journeys card in Patient Workspace.
- Recent Visits card in Patient Workspace.
- Sprint 3.3 tests and documentation.

### Not Added Yet

- Timeline.
- Visit templates by type.
- OITI sheet.
- Pregnancy details.
- Ultrasound.
- Investigations.
- Prescription.
- Appointment integration.
# Changelog

## 2026-07-07 — Stage 3 / Sprint 3.2 Journey Module

### Added

- Journey model.
- Journey service.
- Journey forms.
- Journey routes.
- Journey templates.
- Journey outcomes by type.
- Lost to follow-up outcome.
- Flexible end date parsing for YYYY, YYYY-MM, and YYYY-MM-DD.
- Journey close/reopen workflow.
- Journey tests.
- Sprint 3.2 documentation.

### Not Added Yet

- Visit linkage.
- Timeline.
- Partner.
- Pregnancy details.
- Infertility cycle details.
- OITI sheet.
- Ultrasound.
- Investigations.
- Appointment integration.
# Changelog

## 2026-07-07 — Stage 3 / Sprint 3.1 Visit Model & Migration

### Added

- Visit model.
- VisitAuditLog model.
- Visit service.
- Visit type/status validation.
- Structured clinical note fields.
- Complete Visit service with confirmation.
- Reopen Visit service with confirmation.
- Doctor/Admin-only reopen rule.
- Minimal visit audit logs for complete/reopen.
- Visit model tests.
- Visit migration.
- Sprint 3.1 documentation.

### Not Added Yet

- Visit UI.
- Journey model.
- Link Visit to Journey.
- Timeline.
- OITI sheet.
- Specialized Visit templates.
- Prescription.
- Investigations.
- Ultrasound.
- Appointment integration.
# Changelog

## 2026-07-07 — Stage 2 / Sprint 2.4 Patient Workspace v1

### Added

- Refined Patient Workspace header.
- MRN/name/age/phone/address identity display.
- Name display using system language setting.
- Virgin badge/check display.
- Clinical Snapshot placeholder.
- Recent Visits placeholder.
- Quick Actions section.
- Disabled New Visit and Visits placeholders.
- Patient Workspace tests.
- Sprint 2.4 documentation.

### Not Added Yet

- Real Visit implementation.
- Timeline implementation.
- Clinical notes.
- Appointments.
- Investigations.
- Documents.
- Partner module.
# Changelog

## 2026-07-07 — Stage 2 / Sprint 2.3 Patient Search

### Added

- Patient search service helpers.
- Patient search route.
- HTMX search input on patient index.
- Patient search results partial.
- Patient result card partial.
- Recent patients for empty search.
- Tests for Arabic name, English name, MRN, padded MRN, phone, duplicate phone, and empty search.
- Sprint 2.3 documentation.

### Changed

- Cleaned patient CRUD tests to use `db.session.get()` instead of legacy `Query.get()`.

### Not Added Yet

- Global topbar search.
- Advanced filters.
- Pagination.
- Appointments.
- Visits.
- Clinical notes.
- Timeline.
# Changelog

## 2026-07-07 — Stage 2 / Sprint 2.2 Patient CRUD

### Added

- Patients blueprint.
- Patient registration form.
- Patient edit form.
- MRN change form.
- Patient list page.
- New patient page.
- Patient detail/workspace shell.
- Patient edit page.
- Admin-only MRN change route with warning confirmation.
- Duplicate phone warning.
- Patient CRUD tests.
- Sprint 2.2 documentation.

### Not Added Yet

- Patient live search.
- Appointments.
- Visits.
- Clinical notes.
- Timeline.
- Documents.
- Partner.
# Changelog

## 2026-07-07 — Stage 2 / Sprint 2.1 Patient Model & Migration

### Added

- Patient model.
- UUID internal patient identifier.
- Integer medical file number.
- 6-digit MRN display helper.
- Arabic and English patient names.
- Patient search name foundation.
- DOB/manual age display logic.
- Virgin checkbox field.
- Patient service.
- Patient model tests.
- Sprint 2.1 documentation.

### Not Added Yet

- Patient CRUD UI.
- Patient search UI.
- Patient workspace UI.
- Appointment implementation.
- Visit implementation.
- Clinical notes.
- Audit table.
- Partner module.
- National ID.
# Changelog

## 2026-07-06 — Stage 1 / Sprint 1.3 Settings Foundation

### Added

- Setting model.
- Settings service.
- Grouped default settings.
- Admin-only settings page.
- Settings update flow.
- Public settings reader.
- Settings seed command.
- Settings tests.
- Sprint 1.3 documentation.

### Not Added Yet

- Audit.
- Patient CRUD.
- Appointment CRUD.
- Visit CRUD.
- Real clinical modules.
- AI features.
# Changelog

## 2026-07-06 — Stage 1 / Sprint 1.2 Multi-role RBAC

### Added

- Role model.
- Permission model.
- User-role association table.
- Role-permission association table.
- Multi-role user support.
- RBAC service.
- Permission decorator.
- 403 access denied page.
- Admin placeholder route.
- Clinical placeholder route for RBAC testing only.
- Reception placeholder route for RBAC testing only.
- Role/permission seed command.
- RBAC tests.
- Sprint 1.2 documentation.

### Not Added Yet

- Audit.
- Settings UI.
- Patient CRUD.
- Appointment CRUD.
- Visit CRUD.
- Real clinical modules.
- AI features.
# Changelog

## 2026-07-06 — Stage 1 / Sprint 1.1 Auth + Admin Seed

### Added

- User model.
- Password hashing.
- Email or phone login.
- Login route.
- Logout route.
- Protected dashboard.
- Admin seed command.
- Login template.
- Auth service.
- Login form.
- Auth tests.
- User migration.
- Sprint 1.1 documentation.

### Not Added Yet

- RBAC.
- Roles.
- Permissions.
- Audit.
- Patients.
- Appointments.
- Visits.
- Clinical modules.
- Settings UI.
- AI features.

## 2026-07-06 — Stage 0 / Sprint 0.3 Migration and PWA Placeholder Closure

### Added

- Flask-Migrate / Alembic migration structure.
- PWA placeholder manifest.
- PWA placeholder service worker.
- Base template manifest reference.
- Base template service worker registration.
- PWA placeholder tests.
- Sprint 0.3 documentation.

## 2026-07-06 — Stage 0 / Sprint 0.2 UI Shell Foundation

### Added

- Clinic OS sidebar shell.
- Topbar layout.
- Mobile sidebar behavior using Alpine.js.
- Placeholder navigation for Dashboard, Today Clinic, Patients, Appointments, Visits, Investigations, Reports, and Settings.
- Dashboard placeholder cards for future clinic modules.
- HTMX-ready main content area.
- UI shell tests.
- Sprint 0.2 documentation.

## 2026-07-06 — Stage 0 / Sprint 0.1 Foundation

### Added

- Flask app factory.
- Configuration system.
- Extension registry.
- SQLAlchemy setup.
- Flask-Migrate setup.
- Flask-Login setup.
- CSRF setup.
- Main blueprint.
- `/` foundation page.
- `/health` endpoint.
- Bootstrap 5 base template.
- HTMX script.
- Alpine.js script.
- Basic static CSS and JS.
- Basic 404 and 500 templates.
- Initial pytest health tests.
- README baseline.
- `.env.example`.
- `.gitignore`.












## 2026-07-07 — Sprint 4.1 Appointment Model & Migration

### Added
- Appointment model.
- Appointment service.
- Appointment workflow validation.
- Emergency unscheduled appointment support.
- End-of-day no-show conversion.
- Appointment counters for clinic day.
- Sprint 4.1 tests and documentation.


## 2026-07-07 — Sprint 4.2 Appointment Booking + Calendar View
### Added
- Appointment booking routes and forms.
- Appointment list and detail pages.
- Calendar month/week/day views.
- Patient appointment booking route.
- Patient appointment history page.
- Appointment CRUD/calendar tests.
- Sprint 4.2 documentation.

## 2026-07-07 — Sprint 4.3 Arrival / Waiting Queue
### Added
- Mark appointment arrived route.
- Cancel appointment route.
- Reschedule appointment route.
- Emergency unscheduled appointment route.
- Waiting queue service.
- Appointment workflow tests.
- Sprint 4.3 documentation.

### Confirmed
- Appointment workflow does not create Visit automatically.
- Patient Workspace remains doctor-first.

## 2026-07-07 — Sprint 4.4 Today’s Clinic Dashboard
### Added
- Today’s Clinic blueprint.
- Today’s Clinic dashboard route.
- Clinic day route.
- End-of-day close route.
- Mark appointment completed route.
- Smart clinic day counters.
- Waiting queue section.
- Full day appointment list.
- Patient preview cards.
- Active Journey badges.
- Last Visit display.
- Pending flags placeholder.
- Sprint 4.4 tests and documentation.

### Confirmed
- Today’s Clinic does not create Visit automatically.
- Appointment remains visible after status changes.
- End-of-day close converts remaining booked appointments to no-show.

## 2026-07-12 — Sprint 4.5 Previous Days Clinic
### Added
- Previous clinic days route.
- Past clinic day summary route behavior.
- Previous day summary cards.
- No-show history review.
- Arrived-but-not-completed review.
- Completed appointment review.
- Cancelled/rescheduled appointment review.
- Unfinished work placeholder.
- Sprint 4.5 tests and documentation.

### Confirmed
- Previous Days Clinic is generated from appointments.
- No separate clinic-day table was added.
- Today’s Clinic remains focused on the selected current day.

## 2026-07-12 — Sprint 4.6 Stage 4 Freeze
### Confirmed
- Stage 4 Appointment & Today’s Clinic workflow frozen.
- Appointment model belongs to Patient.
- Appointment types are fixed and billing-ready.
- Procedure remains deferred as a Visit add-on.
- Booking, calendar, arrival, waiting, cancel, reschedule, emergency unscheduled, no-show conversion, Today’s Clinic, and Previous Days Clinic are verified.
- Appointment does not create Visit automatically.
- Doctor can open Patient Workspace and start Visit manually.
- Previous clinic days can be reviewed.
- No billing implementation added.
- No unrelated features added.

### Verification
- 175 tests passed.
- Migration head clean: ecf98d78d1b4.
- Git working tree clean before freeze documentation.

## 2026-07-12 — Sprint 5.1A Drug Dictionaries Backend Foundation
### Added
- DrugCategory model.
- DrugForm model.
- DrugRoute model.
- DrugSafetyStatus model.
- DrugDictionaryService.
- Default medication dictionary seed method.
- `drug_settings.manage` permission.
- Alembic migration `20260712_0051_add_drug_dictionaries`.
- Drug dictionary model and CRUD/service tests.

### Confirmed
- Admin and Doctor can manage drug settings.
- Reception is blocked from drug settings.
- No Drug model added yet.
- No Prescription model added yet.
- No UI or print engine added yet.

### Verification
- 187 tests passed.
- Migration current/head: `20260712_0051`.

## 2026-07-12 — Sprint 5.1B Drug Settings UI
### Added
- Drug Settings blueprint.
- Drug dictionary forms.
- Drug Settings index template.
- Drug dictionary create/edit template.
- Sidebar link for Drug Settings.
- Seed defaults UI action.
- Deactivate/reactivate UI actions.
- UI tests for drug settings permissions and workflows.

### Confirmed
- Doctor/Admin can manage medication dictionaries.
- Reception is blocked.
- Drug settings routes are registered.
- No Drug model added yet.
- No Prescription model added yet.
- No print engine added yet.

### Fixed
- Avoided Jinja `dictionary.items` collision by using `records` in the template context.

### Verification
- 195 tests passed.
- Migration current/head: `20260712_0051`.

## 2026-07-12 — Sprint 5.2A Drug Database Backend Foundation
### Added
- Drug model.
- DrugService.
- Drugs migration `20260712_0052_add_drugs`.
- Relationships from drugs to categories, forms, routes, and safety statuses.
- Duplicate prevention for `trade_name + form_id + strength`.
- Drug model tests.
- Drug service tests.

### Changed
- Updated old dictionary test now that the Drug model exists.

### Confirmed
- Drug database backend exists.
- Drug UI was not added.
- Prescription model was not added.
- Prescription UI was not added.
- Print engine was not added.

### Verification
- 210 tests passed.
- Migration current/head: `20260712_0052`.

## 2026-07-13 — Sprint 5.2B Drug Database UI
### Added
- Drug Database blueprint.
- Drug form.
- Drug list and search page.
- Drug create/edit template.
- Drug deactivate/reactivate actions.
- Sidebar link for Drug Database.
- UI tests for drug database access and workflows.

### Changed
- DrugService supports clearing optional drug relationships during edit.
- Appointment timestamp defaults now use timezone-aware UTC callables instead of deprecated `datetime.utcnow`.

### Confirmed
- Doctor/Admin can manage drugs.
- Reception is blocked.
- Drug search works by trade name, generic name, and strength.
- Duplicate drug combination remains rejected.
- Drug routes are registered.
- No Prescription model added.
- No Prescription UI added.
- No print engine added.

### Verification
- 217 tests passed.
- Warnings cleaned.
- Migration current/head: `20260712_0052`.

## 2026-07-13 — Sprint 5.3A Prescription Backend Foundation
### Added
- Prescription model.
- PrescriptionItem model.
- PrescriptionService.
- Prescription permissions:
  - prescriptions.view
  - prescriptions.manage
- Alembic migration 20260713_0053.
- Prescription model tests.
- Prescription service tests.
- Sprint 5.3A documentation.

### Confirmed
- Prescription belongs to Visit.
- Prescription belongs to the same Patient as Visit.
- One Visit has one Prescription initially.
- PrescriptionItem uses active Drug from Drug Database.
- Dose, frequency, duration, and Arabic instructions are structured.
- Reception is blocked from prescription permissions.
- No Appointment-linked prescription added.
- No Prescription UI added.
- No presets added.
- No print engine added.

### Verification
- 231 tests passed.
- Migration current/head: `20260713_0053`.

## 2026-07-13 — Sprint 5.4A Prescription UI Inside Visit
### Added
- Prescription section inside Visit detail.
- PrescriptionItemForm.
- Add medication item route.
- Edit medication item route.
- Remove medication item route.
- Medication item edit template.
- Prescription UI tests.
- Sprint 5.4A documentation.

### Confirmed
- Doctor can see Prescription section inside Visit detail.
- Doctor can add structured medication items.
- Doctor can edit structured medication items.
- Doctor can remove medication items.
- Reception is blocked from clinical Visit detail and prescription workflows.
- Active drugs are used for medication selection.
- Route override uses active routes.
- No print engine added.
- No presets added.
- No diagnosis added.
- No migration required.

### Verification
- Prescription UI tests: 6 passed.
- Prescription model/service/UI tests: 20 passed.
- Full suite: 237 passed.
- Migration current/head: `20260713_0053`.

2026-07-13 — Sprint 5.5A Prescription Presets Backend Foundation
Added
PrescriptionPreset model.
PrescriptionPresetItem model.
PrescriptionPresetService.
Preset creation, update, activation/deactivation, item management, and application to prescription.
prescription_presets.manage permission.
Migration 20260713_0054_add_prescription_presets.
Preset model and service tests.
Sprint 5.5A documentation.
Confirmed
Presets are global.
Preset items are structured.
Applying a preset creates editable PrescriptionItem rows.
Doctor/Admin can manage presets.
Reception remains blocked.
No preset UI added.
No print engine added.
No diagnosis-linked preset behavior added.

## 2026-07-13 — Sprint 5.5B Prescription Presets Management UI
### Added
- Prescription presets management blueprint.
- Preset list, create, edit, activate, and deactivate UI.
- Preset detail page with structured medication items.
- Add, edit, and remove preset medication item UI.
- Sidebar link for Prescription Presets.
- UI tests for preset management access and workflows.
- Sprint 5.5B documentation.

### Confirmed
- Doctor/Admin can manage presets.
- Reception remains blocked.
- No apply-to-visit UI added.
- No print engine added.
- No migration added.

## 2026-07-13 — Sprint 5.5C Apply Prescription Preset Inside Visit UI
### Added
- Apply-preset form inside Visit prescription card.
- Active prescription preset dropdown.
- Visit route for applying preset to a Visit prescription.
- UI tests for applying presets from Visit detail.
- Sprint 5.5C documentation.

### Confirmed
- Applying a preset creates editable prescription items.
- Prescription is created automatically if missing.
- Doctor/Admin can apply presets through prescription permissions.
- Reception remains blocked.
- Empty preset application shows an error.
- No print engine added.
- No migration added.
- No AI or diagnosis-linked behavior added.

## 2026-07-13 — Sprint 5.6 Prescription Print Engine v1
### Added
- Prescription print route from Visit.
- Standalone prescription print template.
- Print button inside Visit prescription card when medications exist.
- Browser print layout with patient name, MRN, date, and medication lines.
- UI tests for print page, print button, empty prescription redirect, and Reception blocking.
- Sprint 5.6 documentation.

### Confirmed
- No diagnosis printed.
- No doctor identity printed.
- No print lock added.
- No print history added.
- Reception print access remains blocked.
- No migration added.

## 2026-07-13 — Sprint 5.7 Prescription Module Freeze Review
### Changed
- Fixed duplicate mobile sidebar Prescription Presets link.
- Updated sidebar footer from Stage 4 Appointments to Stage 5 Prescriptions.
- Cleaned mojibake strings in prescription UI tests.
- Added final prescription freeze regression checks.
- Added Sprint 5.7 freeze documentation.

### Confirmed
- Stage 5 prescription foundation remains stable.
- No new database migration added.
- No diagnosis printed.
- No doctor identity printed.
- No safety notes printed.
- Reception remains blocked from treatment workflow.
- No print locking, print history, PDF generation, or AI prescribing added.

## 2026-07-13 — Sprint 6.1A Investigation Dictionaries + Core Models
### Added
- Investigation category and test models.
- Investigation order and order item models.
- Investigation result model.
- Support for historical/external results without prior order.
- Support for separate ordered visit and result visit.
- Lab name, result date, result value/unit/reference range/text, doctor comment, abnormal flag, and attachment placeholder fields.
- Investigation dictionary and investigation services.
- Latest result, pending ordered result, and missing test service helpers.
- Investigation RBAC permissions for Doctor/Admin.
- Migration `20260713_0061_add_investigation_core`.
- Model/service tests and Sprint 6.1A documentation.

### Confirmed
- No UI added.
- No presets added.
- No print request added.
- No real file upload/storage added.
- No lab integration added.
- No AI behavior added.

## 2026-07-13 — Sprint 6.1B Investigation Orders From Visit UI
### Added
- Investigation forms.
- Investigation blueprint and routes.
- Create investigation order from Visit workflow.
- Investigation order detail page.
- Add individual test to investigation order workflow.
- Cancel investigation item workflow.
- Patient investigations page with pending/latest sections.
- Visit detail investigations section.
- Sidebar Investigations link.
- UI tests and Sprint 6.1B documentation.

### Confirmed
- No result entry UI added.
- No historical result UI added.
- No presets added.
- No print request added.
- No upload/storage added.
- No AI behavior added.
- No migration added.

## 2026-07-13 — Sprint 6.2A Investigation Presets Backend
### Added
- InvestigationPreset and InvestigationPresetItem models.
- InvestigationPresetService.
- Apply-preset-to-order backend workflow.
- Missing tests from preset using latest patient results.
- Duplicate preset name prevention.
- Duplicate test-in-preset prevention.
- Duplicate active order test prevention during preset apply.
- `investigation_presets.manage` permission for Doctor/Admin.
- Migration `20260713_0062_add_investigation_presets`.
- Model/service tests and Sprint 6.2A documentation.

### Confirmed
- No preset UI added.
- No result entry UI added.
- No historical result UI added.
- No print request added.
- No upload/storage added.
- No AI behavior added.

## 2026-07-13 — Sprint 6.2B Investigation Presets UI
### Added
- Investigation preset forms.
- Investigation presets blueprint/routes.
- Preset list/create/edit/detail UI.
- Add/remove preset investigation tests.
- Apply investigation preset from order detail.
- Sidebar Investigation Presets link.
- UI tests and Sprint 6.2B documentation.

### Confirmed
- No result entry UI added.
- No historical result UI added.
- No print request added.
- No upload/storage added.
- No AI behavior added.
- No migration added.

## 2026-07-13 — Sprint 6.3 Investigation Result Entry
### Added
- Hardened InvestigationService result entry logic.
- Result update/cancel/listing helpers.
- Ordered result entry form and route.
- Historical/external result entry from Patient and Visit.
- Result display in investigation order detail and patient investigations.
- Result entry UI tests and backend service tests.
- Sprint 6.3 documentation.

### Confirmed
- No result review UI added.
- No print request added.
- No upload/storage added.
- No timeline integration added.
- No AI behavior added.
- No migration added.

## 2026-07-13 — Sprint 6.4 Result Review and Patient Workspace
### Added
- InvestigationReviewForm.
- Pending result review page.
- Result review POST route.
- Review note, reviewed_by_user, reviewed_at, and abnormal flag confirmation workflow.
- Patient Workspace investigation section.
- Pending ordered results in Patient Workspace.
- Pending review results in Patient Workspace.
- Latest results in Patient Workspace.
- Missing workup check from investigation preset.
- Generated timeline investigation ordered/result/reviewed events.
- Review service/UI tests and Sprint 6.4 documentation.

### Confirmed
- No migration added.
- No AI interpretation added.
- No automatic diagnosis added.
- No upload/storage added.
- No lab integration added.
- No print request added.

## 2026-07-13 — Sprint 6.5A Unified Print Template Backend
### Added
- Generic PrintTemplate model.
- print_templates table migration.
- PrintTemplateService.
- JSON layout storage for visual print designer positions.
- Prescription and investigation_request document types.
- Default template helpers.
- print_templates.manage permission.
- Print template model/service/RBAC tests.
- Sprint 6.5A documentation.

### Confirmed
- Existing prescription print remains temporarily until Sprint 6.5C migration.
- No visual designer UI added.
- No prescription print route migration added.
- No investigation print route added.
- No print preview added.
- No PDF generation added.
- No print history added.
- No print lock added.
- No doctor signature added.
- No AI behavior added.

## 2026-07-13 — Sprint 6.5B Unified Visual Designer UI
### Added
- Print Templates blueprint and routes.
- PrintTemplateForm.
- Print template list/create/edit/deactivate/reactivate UI.
- Seed default print templates action.
- Generic visual designer page.
- Drag-and-drop element positioning on paper canvas.
- layout_json save workflow.
- Sidebar Print Templates link.
- Print template UI tests.
- Sprint 6.5B documentation.

### Confirmed
- No new migration added.
- Existing prescription print remains temporarily until Sprint 6.5C migration.
- No investigation print route added.
- No print preview rendering added.
- No PDF generation added.
- No print history added.
- No print lock added.
- No doctor signature added.
- No AI behavior added.

## 2026-07-13 — Sprint 6.5C Prescription Migration to Unified Print
### Added
- Unified prescription print preview route.
- Unified prescription designer redirect route.
- PrintTemplate-based prescription preview rendering.
- Optional template_uuid support for prescription preview.
- Dedicated unified prescription print tests.
- Sprint 6.5C documentation.

### Changed
- Visit prescription Print button now points to unified /print/prescriptions/ preview.
- Prescription print tests now validate unified print behavior.

### Removed
- Legacy visits.print_prescription route.
- Legacy visits/prescription_print.html template.

### Confirmed
- No new migration added.
- No investigation print route added.
- No PDF generation added.
- No print history added.
- No print lock added.
- No doctor signature added.
- No AI behavior added.

## 2026-07-13 — Sprint 6.5D Investigation Print Using Unified Designer
### Added
- Unified investigation request print preview route.
- Unified investigation request designer redirect route.
- PrintTemplate-based investigation request rendering.
- Optional template_uuid support for investigation request preview.
- Print request button on investigation order detail.
- Dedicated unified investigation print tests.
- Sprint 6.5D documentation.

### Changed
- Cleaned prescription print line separator text.

### Confirmed
- No new migration added.
- No result report printing added.
- No PDF generation added.
- No print history added.
- No print lock added.
- No doctor signature added.
- No lab integration added.
- No AI behavior added.

## 2026-07-13 — Sprint 6.5E Print Module Freeze Review
### Verified
- PrintTemplate backend and service layer.
- PrintTemplate management UI and visual designer.
- Unified prescription print preview.
- Unified investigation request print preview.
- Print route registration.
- RBAC blocking for Reception.
- Documentation coverage.
- Migration head remains 20260713_0063.

### Confirmed Out of Scope
- PDF generation.
- Print history.
- Print lock.
- Doctor signature.
- Logo upload.
- Result report printing.
- Lab integration.
- AI behavior.

## 2026-07-13 — Stage 6 Investigation Module Freeze Review
### Verified
- Investigation dictionaries, tests, orders, and order items.
- Investigation presets backend and UI.
- Ordered and historical investigation result entry.
- Result review workflow and pending review queue.
- Patient Workspace investigation section.
- Timeline investigation events.
- Unified investigation request printing.
- Stage 5 prescription regression after unified print migration.
- RBAC and Reception blocking.
- Migration head remains 20260713_0063.

### Changed
- Cleaned investigation test choice label separator in Visit detail.

### Confirmed Out of Scope
- Real upload/storage.
- Result report printing.
- PDF generation.
- Lab integration.
- Alerts/notifications.
- Billing/finance.
- AI interpretation.

## 2026-07-13 — Sprint 6.6A Enter Pending Result From Current Visit
### Added
- Current-Visit ordered investigation result entry route.
- Visit detail action for pending results from previous visits.
- Regression tests proving ordered_visit and result_visit can differ.

### Changed
- Ordered investigation result entry can now preserve original ordered Visit while storing the current Visit as result Visit.

### Confirmed
- No migration added.
- Investigation dictionary/settings UI remains deferred.
- Upload/storage, lab integration, and AI remain out of scope.

## 2026-07-13 — Sprint 7.1 Documents Backend Foundation
### Added
- PatientDocument model.
- DocumentService for local file storage and metadata.
- File validation and secure stored filename generation.
- Optional document links to Visit and InvestigationResult.
- Document RBAC permissions for Admin and Doctor.
- Migration 20260713_0064.
- Backend model/service tests.
- Sprint 7.1 documentation.

### Confirmed Out of Scope
- UI.
- OCR.
- AI extraction.
- Cloud storage.
- Drawing tools.
- Ultrasound module.

## 2026-07-13 — Sprint 7.2 Patient Documents UI
### Added
- Documents blueprint and routes.
- Document upload form.
- Patient document list page.
- Document detail page.
- Secure document download route.
- Document archive route.
- Patient Workspace documents section.
- Document UI tests.
- Sprint 7.2 documentation.

### Confirmed Out of Scope
- OCR.
- AI extraction.
- Cloud storage.
- Drawing/annotation.
- Ultrasound module.
- Investigation result attachment UI.

## 2026-07-13 — Sprint 7.3 Attach Documents to Investigation Results
### Added
- InvestigationResult document upload route.
- PatientDocument linkage to InvestigationResult.
- Attached report display on investigation order detail.
- Attached report display on patient investigations page.
- Improved document detail investigation result link.
- Investigation document attachment tests.
- Sprint 7.3 documentation.

### Confirmed Out of Scope
- OCR.
- AI extraction.
- Lab integration.
- Result interpretation.
- PDF parsing.
- Drawing/annotation.
- Cloud storage.

## 2026-07-13 — Stage 7 Documents & Storage Freeze Review
### Verified
- PatientDocument model and migration.
- DocumentService local storage workflow.
- Secure filename and file validation.
- Patient document upload, list, detail, download, and archive.
- Patient Workspace documents section.
- InvestigationResult report attachment.
- RBAC for documents.view and documents.manage.
- Reception blocked from document workflows.
- No migration drift.
- No OCR, AI extraction, cloud storage, drawing tools, lab integration, or PDF parsing.

### Next
- Stage 8 Ultrasound.

## 2026-07-14 — Sprint 8.1 Ultrasound Backend Foundation

### Added
- ClinicUltrasoundExam model.
- ExternalUltrasoundRequest model.
- ClinicUltrasoundService.
- ExternalUltrasoundService.
- Ultrasound RBAC permissions.
- Ultrasound backend migration.
- Sprint 8.1 model and service tests.

### Notes
- Clinic ultrasound date is derived from the linked Visit.
- No exam_date field was added.
- No external ultrasound result table was added.

## 2026-07-15 — Sprint 8.2 Inline Clinic Ultrasound Visit UI

### Added
- Inline clinic ultrasound form inside Visit Detail.
- Inline clinic ultrasound edit inside Visit cards.
- Clinic ultrasound cards inside Visit Detail.
- Light clinic ultrasound summary inside Patient Workspace.
- Clinic ultrasound UI tests.

### Notes
- No new migration.
- No separate ultrasound new/edit/detail pages.
- No exam_date field.
- No plan field inside ultrasound.
- External ultrasound request/upload remains deferred to Sprint 8.3.

## 2026-07-15 — Sprint 8.3 External Ultrasound Request + Upload

### Added
- External US request form inside Visit Ultrasound section.
- Category/modality multi-select for external US requests.
- Direct external US result workflow.
- Pending request completion with file or note-only result.
- Image thumbnail preview route for patient documents.
- Patient Workspace external ultrasound request/result summaries.
- Sprint 8.3 UI tests.

### Changed
- Extended ExternalUltrasoundRequest with request metadata and result note.

### Migration
- Added `20260715_0066_external_ultrasound_request_upload_metadata.py`.

## 2026-07-15 — Stage 8 Ultrasound Frozen

### Frozen
- Stage 8 Ultrasound accepted as complete.
- Verified clinic ultrasound, external ultrasound request, external upload, note-only result, thumbnails, Patient Workspace summary, RBAC, migration, and documentation.
- Final regression: 407 passed.
- Migration head: 20260715_0066.
- Last Sprint 8 commit: 1fa5b88.

### Next
- Stage 9 Surgery.

## 2026-07-15 — Stage 9 Surgery Module

### Added
- SurgeryCase model and migration.
- Surgery service and status workflow.
- Surgery dashboard/list/calendar/detail UI.
- Create surgery from dashboard, patient, or visit context.
- Complete/cancel/postpone workflows.
- Patient Timeline surgery events.
- Patient Surgical History section.
- Basic module-level surgery analytics.
- Surgery RBAC permissions.

### Deferred
- Surgery documents/consent.
- Operation report print.
- Full finance module.
- AI/OCR.

## 2026-07-15 — Stage 9 Surgery Freeze Cleanup

### Added
- Postponed / Cancelled section on Surgery Dashboard.
- Mark Scheduled action for postponed surgeries.
- Freeze review document for Stage 9 Surgery.

### Verified
- Surgery workflow cleanup tests.
- RBAC and patient workspace regression.
- Full suite expected before freeze.

## 2026-07-15 — Stage 10 Partner Module

### Added
- Partner model and Patient Workspace section.
- PartnerSemenAnalysis notes/upload history.
- `semen_analysis` document type.
- Prescription target support for patient/partner.
- Partner prescription workflow using existing medication items.
- Stage 10 tests and documentation.

### Deferred
- Structured SA parameters.
- OCR/AI SA interpretation.
- Partner prescription printing.
- Partner dashboard.

## 2026-07-15 — Stage 11 Embedded Finance

### Added
- FinanceCharge, FinancePayment, and FinanceExpense models.
- FinanceService for embedded income and expenses.
- Appointment embedded payment fields.
- Visit embedded payment fields.
- Surgery payment method and finance sync.
- Finance dashboard and expenses page.
- Patient Workspace finance card.
- Finance permissions and tests.

### Deferred
- Advanced insights/charts.
- Refunds.
- Full accounting ledger.
- Export.

## 2026-07-15 — Stage 11.2 Finance Insights

### Added
- Finance insights date-range dashboard.
- Revenue by service type.
- Expenses by category.
- Payment method breakdown.
- Daily finance summary.
- Outstanding balances table.
- Finance insights tests.

### Unchanged
- No migration required.
- No refunds/export/accounting ledger added.

## 2026-07-15 — Stage 11 Finance Frozen

### Frozen
- Stage 11 Finance completed and frozen.
- Embedded finance capture verified.
- Finance insights dashboard verified.
- Full regression passed: 425 tests.
- Migration current/head: 20260715_0069.

## 2026-07-15 — Sprint 12.1 Settings UI Foundation

### Added
- Settings dashboard at `/settings/`.
- Grouped settings pages.
- Single setting edit workflow.
- Seed defaults action.
- Appearance personalization keys.
- Localization language choices.
- Stage 12 settings UI tests.
- Stage 12 documentation.

### Unchanged
- No new database table.
- No migration required.
- Legacy `/admin/settings` behavior preserved.

## 2026-07-15 — Sprint 12.2 Appearance, Night Mode, RTL Foundation

### Added
- Global UI preferences context processor.
- Dynamic `html` language, direction, theme, accent, font, and density attributes.
- Dark mode CSS variable foundation.
- Auto theme foundation using system color preference.
- Accent color CSS variables.
- Basic RTL layout foundation.
- Appearance personalization tests.

### Unchanged
- No database schema migration.
- No full Arabic translation yet.
- No per-user preferences yet.

## 2026-07-15 — Sprint 12.3 Clinic Profile Settings

### Added
- Dedicated `/settings/clinic-profile` page.
- Clinic profile helper methods in SettingsService.
- Global clinic profile template context.
- Base shell brand/title support for clinic name and short name.
- Clinic Profile shortcut card on Settings dashboard.
- Sprint 12.3 clinic profile tests and documentation.

### Unchanged
- No database schema migration.
- No logo upload/storage yet.
- No doctor profile table yet.

## 2026-07-15 — Sprint 12.4 Workflow Defaults

### Added
- Workflow landing resolver in SettingsService.
- Successful login redirect support for `workflow.default_landing_page`.
- Workflow defaults summary on Settings dashboard.
- Sprint 12.4 workflow default tests and documentation.

### Unchanged
- No database schema migration.
- No dashboard/admin redesign in this sprint.
- No per-user preferences yet.

## 2026-07-15 — Stage 12 Settings & Personalization Freeze Review

### Frozen
- Settings UI Foundation.
- Appearance, Night Mode, and RTL foundation.
- Clinic Profile Settings.
- Workflow Defaults.
- Settings RBAC protection.
- Stage 12 tests and documentation.

### Verified
- Settings dashboard and grouped settings editor.
- Single setting edit workflow.
- Seed defaults action.
- Global UI preferences context.
- Clinic profile context and page.
- Login redirect via workflow.default_landing_page.
- No migration drift.

### Deferred
- Full Arabic translation.
- Per-user preferences.
- Logo upload pipeline.
- Notifications.
- Advanced permission builder.
- Complex theme designer.

## 2026-07-15 — Project Pause After Stage 12

### Added
- Project handoff document for pausing after Stage 12.
- Real personal trial checklist.
- Next-chat continuation instructions.
- README current status block.
- MEMORY update for paused development state.

### Decision
- Stop feature development temporarily.
- Test the system in real personal clinic-style use.
- Collect workflow/UX/bug notes before Stage 13 or any new module.

### Latest Known Good State
- Latest freeze commit before handoff: cb73a9a.
- Migration current/head: 20260715_0069.
- Full regression at Stage 12 freeze: 450 passed.

## 2026-07-16 - Personal Trial Sprint P1 - Application Shell Baseline

### Added
- Operational clinic dashboard backed by DashboardService.
- Searchable and status-filtered Visits index.
- Permission-aware desktop and mobile navigation.
- Collapsible desktop sidebar.
- Regression tests for dashboard, Visits, Reception access, and print isolation.

### Changed
- Removed obsolete development-stage wording from the shell.
- Protected clinical dashboard content from Reception users.
- Preserved print previews without authenticated doctor identity.

### Verification
- Full regression: 455 passed.
- Migration current/head: 20260715_0069.
- No database or migration changes.
- Implementation commit: ce5b454.

### Trial Follow-up
- Redesign the collapsed sidebar as a hover-expand overlay with optional pin.
- Replace basic counters with an advanced role-aware clinic dashboard.