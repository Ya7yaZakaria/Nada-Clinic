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
