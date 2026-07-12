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
