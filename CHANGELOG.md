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
