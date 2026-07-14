# Nada Clinic System

Nada Clinic System is a doctor-first, patient-centered clinic operating system for OB/GYN workflows.

## Current Stage

Stage 1 — Core System Foundation

Completed:
- Stage 0 / Sprint 0.1 — Flask Project Foundation
- Stage 0 / Sprint 0.2 — UI Shell Foundation
- Stage 0 / Sprint 0.3 — Migration and PWA Placeholder Closure
- Stage 1 / Sprint 1.1 — Auth + Admin Seed
- Stage 1 / Sprint 1.2 — Multi-role RBAC

Current:
- Stage 1 / Sprint 1.3 — Settings Foundation

## Stack

- Python
- Flask
- SQLAlchemy
- Alembic / Flask-Migrate
- Flask-Login
- Flask-WTF / CSRF
- HTML5
- Bootstrap 5
- HTMX
- Alpine.js

## Run Locally

1. Create and activate virtual environment.
2. Install requirements.
3. Create local `.env`.
4. Run migrations.
5. Seed first admin.
6. Seed RBAC.
7. Seed settings.
8. Run the Flask app.

Commands:

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
flask seed-admin
flask seed-rbac
flask seed-settings
python run.py

Open:

http://127.0.0.1:5000/
http://127.0.0.1:5000/health
http://127.0.0.1:5000/admin/settings

## Tests

python -m pytest

## Flask CLI

$env:FLASK_APP="app"
flask routes

## Migrations

Alembic / Flask-Migrate is initialized.

Common commands:

flask db current
flask db heads
flask db migrate -m "message"
flask db upgrade

## Admin Seed

The first admin seed user is created locally from `.env`.

Required local variables:

ADMIN_EMAIL
ADMIN_PASSWORD
ADMIN_NAME
ADMIN_PHONE

Never commit `.env`.

## RBAC

RBAC supports multiple roles per user.

Initial roles:

- Admin
- Doctor
- Reception

Initial permissions:

- dashboard.view
- patients.basic.view
- patients.basic.create
- appointments.view
- appointments.manage
- clinical.view
- clinical.note.view
- clinical.note.write
- settings.view
- settings.manage
- admin.access

Seed command:

flask seed-rbac

The first admin seed user receives:

- Admin
- Doctor

## Settings

Settings are grouped and stored in the database.

Groups:

- clinic
- localization
- appearance
- workflow
- printing
- security
- system

Seed command:

flask seed-settings

## Project Philosophy

- Doctor-first
- Patient-centered
- Fast
- Minimal clicks
- Timeline-driven
- AI-ready
- Mobile/iPad friendly

## Current Scope

Implemented:
- Flask foundation
- Base routing
- Health endpoint
- Base templates
- Static assets
- Clinic OS UI shell
- Sidebar placeholder navigation
- Migration setup
- PWA placeholder manifest
- PWA placeholder service worker
- User model
- Login/logout
- Password hashing
- Admin seed command
- Multi-role RBAC
- Roles
- Permissions
- Permission checks
- 403 page
- Settings table
- Grouped settings
- Admin settings page
- Settings seed command
- Tests
- Sprint documentation

Not implemented yet:
- Audit
- Patients
- Appointments
- Visits
- Real clinical modules
- AI layer

## Stage 2 / Sprint 2.1 — Patient Model & Migration

Patient is now introduced as the root clinical entity.

Implemented:

- Patient model
- UUID internal ID
- Integer MRN
- 6-digit formatted MRN display
- Arabic and English names
- Patient search name foundation
- Phone fields
- Address fields: governorate, city, street
- DOB/manual age logic
- Virgin checkbox
- Patient service
- Patient model tests
- Sprint 2.1 documentation

Not implemented yet:

- Patient CRUD UI
- Patient search UI
- Patient workspace UI
- Visits
- Appointments
- Clinical notes
- Audit

## Stage 2 / Sprint 2.2 — Patient CRUD

Implemented:

- Patients blueprint
- Patient form
- MRN change form
- Patient list
- Patient creation
- Patient edit
- Patient detail/workspace shell
- Admin-only MRN edit with warning confirmation
- Duplicate phone warning
- Patient CRUD tests
- Sprint 2.2 documentation

Routes:

- GET /patients/
- GET /patients/new
- POST /patients/new
- GET /patients/<uuid>
- GET /patients/<uuid>/edit
- POST /patients/<uuid>/edit
- POST /patients/<uuid>/mrn

Not implemented yet:

- Patient live search
- Appointments
- Visits
- Clinical notes
- Timeline

## Stage 2 / Sprint 2.3 — Patient Search

Implemented:

- Patient search service helpers
- Patient search route
- HTMX live search input
- Patient search results partial
- Patient result card partial
- Search by Arabic name
- Search by English name
- Search by integer MRN
- Search by padded MRN
- Search by phone
- Empty search shows recent patients
- Duplicate phone search can return multiple patients
- Patient search tests
- SQLAlchemy legacy Query.get warnings cleaned in patient CRUD tests

Route:

- GET /patients/search

Not implemented yet:

- Global topbar search
- Advanced filters
- Pagination
- Appointments
- Visits
- Clinical notes
- Timeline

## Stage 2 / Sprint 2.4 — Patient Workspace v1

Implemented:

- Refined Patient Workspace
- Patient header with MRN/name/age/phone/address
- Name display based on localization.language
- Virgin check display
- Clinical Snapshot placeholder
- Recent Visits placeholder
- Quick Actions section
- Disabled New Visit and Visits placeholders
- Patient Workspace tests
- Sprint 2.4 documentation

Route:

- GET /patients/<uuid>

Not implemented yet:

- Real Visit implementation
- Timeline
- Clinical notes
- Appointments
- Investigations
- Documents
- Partner

## Stage 3 / Sprint 3.1 — Visit Model & Migration

Implemented:

- Visit model
- VisitAuditLog model
- Visit service
- Visit belongs to Patient
- Structured clinical note fields
- Visit type/status validation
- Complete Visit with confirmation
- Reopen Visit with confirmation
- Doctor/Admin-only reopen
- Minimal visit audit logs for complete/reopen
- Visit model tests
- Sprint 3.1 documentation

Not implemented yet:

- Visit UI
- Journey model
- Link Visit to Journey
- Timeline
- OITI sheet
- Specialized Visit templates
- Prescription
- Investigations
- Ultrasound
- Appointment integration

## Stage 3 / Sprint 3.2 — Journey Module

Implemented:

- Journey model
- Journey service
- Journey forms
- Journey routes
- Journey templates
- Outcomes by journey type
- Lost to follow-up outcome
- Flexible end date: YYYY, YYYY-MM, or YYYY-MM-DD
- Close/reopen journey workflow
- Journey tests
- Sprint 3.2 documentation

Not implemented yet:

- Visit linkage
- Timeline
- Partner
- Pregnancy details
- Infertility cycle details
- OITI sheet
- Ultrasound
- Investigations
- Appointment integration

## Stage 3 / Sprint 3.3 — Link Visit to Journey

Implemented:

- Nullable `journey_id` on visits
- Visit to Journey relationship
- Visit creation/edit UI foundation
- Optional Journey selector
- Assign/remove Journey link
- Cross-patient Journey validation
- Standalone Visit warning
- Active Journeys in Patient Workspace
- Recent Visits in Patient Workspace
- Sprint 3.3 tests
- Sprint 3.3 documentation

Not implemented yet:

- Timeline
- Visit templates by type
- OITI sheet
- Pregnancy details
- Ultrasound
- Investigations
- Prescription
- Appointment integration

## Stage 3 / Sprint 3.4 — Timeline Foundation

Implemented:

- Generated TimelineService
- Patient Workspace timeline section
- Journey started events
- Journey closed events
- Visit events
- Visit completed events
- Visit reopened events
- Unassigned Visit marker
- Timeline tests
- Sprint 3.4 documentation

Not implemented:

- Timeline table
- Manual timeline events
- Timeline filters
- Prescription events
- Investigation events
- Ultrasound events
- Appointment events
- Surgery events


## Stage 4 — Appointment & Today's Clinic
Sprint 4.1 adds the Appointment database foundation, workflow service, emergency unscheduled support, end-of-day no-show conversion, and date counters.


## Sprint 4.2 — Appointment Booking + Calendar View
Adds Appointment CRUD routes, AppointmentForm, calendar month/week/day views, patient appointment list, sidebar link, tests, and documentation.

## Workflow Safety Rules

- Do not replace or remove existing workflow actions unless explicitly approved.
- Patient Workspace is doctor-first.
- Patient Workspace must keep clinical actions focused on Visits, Journeys, Timeline, and Patient clinical context.
- Appointment booking is reception/secretary workflow, not doctor Patient Workspace workflow.
- Adding appointment features must not replace existing Visit buttons or placeholders.
- Before changing an existing button, route, template section, status, or workflow meaning, stop and ask for approval.
- Prefer adding new module entry points over modifying unrelated module behavior.
- If a sprint touches files outside its declared scope, explain why before coding.

## Sprint 4.3 — Arrival / Waiting Queue
Adds reception workflow actions for marking appointments arrived, cancellation, rescheduling, emergency unscheduled appointments, and waiting queue service support.

## Sprint 4.4 — Today’s Clinic Dashboard
Adds Today’s Clinic dashboard, day counters, waiting queue, full day appointment list, patient preview cards, active journey badges, last visit display, pending flags placeholder, appointment completion action, and end-of-day close workflow.

## Sprint 4.5 — Previous Days Clinic
Adds previous clinic days review, past day summaries, unfinished work visibility, no-show history review, and generated appointment-based previous-day views without a separate clinic-day table.

## Stage 4 — Appointment & Today’s Clinic Freeze
Stage 4 is frozen after Sprint 4.6. Appointment booking, calendar, arrival/waiting, emergency unscheduled workflow, Today’s Clinic, Previous Days Clinic, end-of-day no-show conversion, and appointment workflow tests are complete. Verified: 175 tests passed, migration head clean, and git working tree clean.

## Sprint 5.1A — Drug Dictionaries Backend Foundation
Sprint 5.1A adds backend foundations for editable, AI-ready medication dictionaries: categories, forms, routes, and safety statuses. It adds `drug_settings.manage` permission for Admin/Doctor access while keeping Reception blocked from treatment-related settings. No Drug model, Prescription model, UI, or print engine was added in this sprint.

## Sprint 5.1B — Drug Settings UI
Sprint 5.1B adds the Drug Settings UI for managing medication dictionaries. Authorized Doctor/Admin users can open Drug Settings, seed defaults, create/edit dictionary items, and deactivate/reactivate them. Reception remains blocked from medication-related settings. No Drug model, Prescription model, or print engine was added.

## Sprint 5.2A — Drug Database Backend Foundation
Sprint 5.2A adds the backend foundation for the clinic drug database. It introduces the Drug model, DrugService, drugs migration, duplicate prevention by trade name + form + strength, relationships to medication dictionaries, and backend tests. No Drug UI, Prescription model, Prescription UI, presets, or print engine was added.

## Sprint 5.2B — Drug Database UI
Sprint 5.2B adds the Drug Database UI. Authorized Doctor/Admin users can list, search, create, edit, deactivate, and reactivate clinic drugs using structured dictionary dropdowns. Reception remains blocked. This sprint also cleans the Appointment timestamp warning by replacing deprecated `datetime.utcnow` defaults with timezone-aware UTC callables. No Prescription model, Prescription UI, presets, or print engine was added.

## Sprint 5.3A — Prescription Backend Foundation
Sprint 5.3A adds the backend foundation for structured prescriptions inside Visits. It introduces Prescription and PrescriptionItem models, a PrescriptionService, prescription permissions, and migration 20260713_0053. Prescriptions belong to Visits, not Appointments. One Visit has one Prescription initially. This sprint does not add Prescription UI, presets, or printing.

## Sprint 5.4A — Prescription UI Inside Visit
Sprint 5.4A adds structured prescription management inside the Visit detail page. Doctors can add, edit, and remove medication items using active drugs from the Drug Database. Reception remains blocked from clinical visit and prescription workflows. This sprint does not add print, presets, diagnosis, or AI prescribing.

Sprint 5.5A — Prescription Presets Backend Foundation

Sprint 5.5A adds backend support for reusable global prescription presets. Presets contain structured medication items and can be applied to an existing prescription to create editable prescription items. This sprint does not add preset UI, print, diagnosis-linked presets, or AI prescribing.

## Sprint 5.5B — Prescription Presets Management UI
Sprint 5.5B adds Doctor/Admin UI for managing reusable prescription presets, including preset list/create/edit/toggle and preset medication item add/edit/remove. It does not add apply-to-visit behavior, print, diagnosis-linked presets, or AI prescribing.

## Sprint 5.5C — Apply Prescription Preset Inside Visit UI
Sprint 5.5C adds an apply-preset control inside the Visit prescription card. Doctor/Admin users can apply an active prescription preset to create editable prescription medication lines. This sprint does not add print, prescription locking, diagnosis-linked suggestions, AI prescribing, or a migration.

## Sprint 5.6 — Prescription Print Engine v1
Sprint 5.6 adds a standalone browser print page for Visit prescriptions. The print page includes patient name, MRN, date, and structured medication lines. It does not add diagnosis, doctor identity, print locking, print history, PDF generation, or a migration.

## Sprint 5.7 — Prescription Module Freeze Review
Sprint 5.7 closes the Stage 5 prescription foundation with a cleanup and freeze review. It fixes duplicate mobile navigation for Prescription Presets, updates the stale sidebar stage label, cleans prescription UI test strings, adds final regression checks, and confirms no migration or unrelated prescription features are introduced.

## Sprint 6.1A — Investigation Dictionaries + Core Models
Sprint 6.1A adds the backend foundation for investigations: categories, tests, orders, order items, results, historical results without prior orders, separate ordered/result visits, latest result lookup, pending ordered result lookup, missing test detection, and investigation RBAC permissions. No UI, presets, print, upload storage, lab integration, or AI behavior is added.

## Sprint 6.1B — Investigation Orders From Visit UI
Sprint 6.1B adds the first investigation UI workflow: doctors can create investigation orders from a Visit, add individual tests, view order details, see pending items from the Visit, and open a Patient Investigations page. It does not add result entry, presets, print requests, upload/storage, AI behavior, or a new migration.

## Sprint 6.2A — Investigation Presets Backend
Sprint 6.2A adds reusable investigation panel/workup backend support. Doctors/Admins can manage investigation presets by service permission, add investigation tests to presets, apply presets to existing investigation orders, and calculate missing tests from presets using latest patient results. No UI, result entry UI, print request, upload/storage, or AI behavior is added.

## Sprint 6.2B — Investigation Presets UI
Sprint 6.2B adds Doctor/Admin UI for investigation preset management and applying presets to investigation orders. Doctors can create presets, add/remove investigation tests, and apply a preset from the investigation order detail page. No result entry, historical result UI, print request, upload/storage, AI behavior, or migration is added.

## Sprint 6.3 — Investigation Result Entry
Sprint 6.3 adds investigation result entry backend and UI. Doctors can enter results for ordered investigation items and record historical/external results from Patient or Visit context. Results store lab name, result date, value/text, doctor comment, abnormal flag, and attachment placeholders. No review UI, print request, upload/storage, AI behavior, timeline integration, or migration is added.

## Sprint 6.4 — Result Review + Patient Workspace
Sprint 6.4 adds investigation result review workflows and Patient Workspace investigation sections. Doctors can review entered results, confirm abnormal flags, store review notes and reviewed timestamps. Patient Workspace now shows pending ordered results, pending review results, latest results, and missing workup from a selected preset. Generated timeline now includes investigation ordered/result/reviewed events. No migration, AI interpretation, lab integration, upload/storage, or print request is added.

## Sprint 6.5A — Unified Print Template Backend
Sprint 6.5A adds the generic PrintTemplate backend foundation for future visual print design. It supports prescription and investigation request document types, millimeter paper sizes, JSON layout storage, active/default templates, service helpers, RBAC permission print_templates.manage, migration, and tests. The existing prescription print route/template remains temporarily until Sprint 6.5C migration. No visual designer UI, prescription route migration, investigation print route, preview, PDF generation, print history, print lock, doctor signature, or AI behavior is added.

## Sprint 6.5B — Unified Visual Designer UI
Sprint 6.5B adds a generic Print Templates UI and visual drag-and-drop designer for reusable print layouts. Doctors/Admins can seed default templates, create/edit templates, open a paper canvas, drag elements, fine-tune positions/sizes, and save layout_json. Existing prescription print remains unchanged until Sprint 6.5C migration. No new migration, prescription route migration, investigation print route, preview rendering, PDF generation, print history, print lock, doctor signature, or AI behavior is added.

## Sprint 6.5C — Prescription Migration to Unified Print
Sprint 6.5C migrates prescription printing from the legacy Visit print page to the unified PrintTemplate-based print engine. The Visit Print button now opens unified prescription preview under /print/prescriptions/, the preview renders medication lines using layout_json, and the old visits/prescription_print.html template plus legacy visit print route are removed. No investigation print route, migration, PDF generation, print history, print lock, doctor signature, or AI behavior is added.

## Sprint 6.5D — Investigation Print Using Unified Designer
Sprint 6.5D adds investigation request printing through the unified PrintTemplate engine. Investigation order detail now exposes a Print request button, and /print/investigations/<order_uuid>/preview renders patient details, request date, instruction text, and ordered investigation lines using layout_json. No migration, result report printing, PDF generation, print history, print lock, doctor signature, lab integration, or AI behavior is added.

## Sprint 6.5E — Print Module Freeze Review
Sprint 6.5E freeze-reviews the unified print module after prescription and investigation request printing were migrated to the PrintTemplate engine. It confirms PrintTemplate backend/UI, visual layout designer, prescription preview, investigation request preview, RBAC, documentation, route health, and no migration drift. PDF generation, print history, print lock, doctor signature, logo upload, result report printing, lab integration, and AI remain out of scope.

## Stage 6 — Investigation Module Freeze Review
Stage 6 freeze review verifies investigation dictionaries, orders, presets, result entry, historical results, result review, patient workspace investigation display, timeline integration, unified investigation request printing, RBAC, and Stage 5 prescription regression after unified print migration. Real upload/storage, result report printing, lab integration, alerts, billing, and AI remain out of scope. Recommended next stage: Stage 7 Documents & Storage.

## Sprint 6.6A — Enter Pending Result From Current Visit
Sprint 6.6A fixes ordered investigation result context. When a patient returns in a later Visit with pending investigation results, the doctor can enter the result from the current Visit. The system preserves the original ordered Visit and stores the current Visit as the result Visit. No migration, dictionary UI, upload/storage, lab integration, or AI behavior is added.

## Sprint 7.1 — Documents Backend Foundation
Sprint 7.1 adds the backend foundation for patient documents: PatientDocument metadata, local file storage, secure filename handling, validation, document service helpers, optional links to Visit and InvestigationResult, RBAC permissions, migration, and backend tests. UI, OCR, AI, cloud storage, drawing tools, and ultrasound workflows remain out of scope.

## Sprint 7.2 — Patient Documents UI
Sprint 7.2 adds UI workflows for patient documents: upload, list, detail, download, archive, and Patient Workspace document display. It reuses the Sprint 7.1 DocumentService and keeps OCR, AI extraction, cloud storage, drawing tools, ultrasound workflows, and investigation result attachment UI out of scope.

## Sprint 7.3 — Attach Documents to Investigation Results
Sprint 7.3 links the Documents module to investigation results. Doctors can upload a real report file from an InvestigationResult context, the file is stored as a PatientDocument linked to the result, and attached reports appear on investigation order and patient investigation pages. OCR, AI extraction, lab integration, PDF parsing, cloud storage, and drawing tools remain out of scope.

## Stage 7 - Documents & Storage Freeze Review
Stage 7 freezes the Documents & Storage module after backend foundation, patient document UI, and investigation result attachment. The module supports local file storage, document metadata, secure filenames, validation, view/download/archive workflows, Patient Workspace integration, InvestigationResult attachment, RBAC, and tests. OCR, AI extraction, cloud storage, drawing tools, lab integration, PDF parsing, and ultrasound structured workflows remain out of scope.

## Stage 8 — Ultrasound Backend Foundation

Sprint 8.1 adds backend foundations for clinic ultrasound records and lightweight external ultrasound requests.

- Clinic ultrasound is linked to Visit.
- Clinic ultrasound date is derived from `Visit.visit_date`.
- No `exam_date` column is added.
- External ultrasound request is a one-textbox pending item.
- External ultrasound result upload will reuse Stage 7 `PatientDocument` in a later sprint.

## Stage 8.2 — Inline Clinic Ultrasound Visit UI

Sprint 8.2 adds inline clinic ultrasound add/edit/archive workflows inside Visit Detail.

- Clinic ultrasound is written directly inside the Visit page.
- Add and edit are inline.
- Ultrasound cards appear inside the Visit.
- Patient Workspace shows a light recent clinic ultrasound summary.
- No exam date field is shown; ultrasound date comes from `Visit.visit_date`.
- No plan field is included in ultrasound.
- No external ultrasound request/upload UI is included yet.

## Stage 8.3 — External Ultrasound Request + Upload

Sprint 8.3 adds external ultrasound request and result workflows inside the Visit Ultrasound section.

- Request US with category/modality multi-select.
- Upload external US report/image from Visit.
- Complete pending request with uploaded file or doctor note only.
- Add direct external US result without prior request.
- Show image thumbnails and PDF/file cards.
- Store files through PatientDocument.
- Store doctor review note on external ultrasound result workflow.
