# Nada Clinic System

Nada Clinic System is a doctor-first, patient-centered clinic operating system for OB/GYN workflows.

## Current Stage

Stage 1 — Core System Foundation

Completed:
- Stage 0 / Sprint 0.1 — Flask Project Foundation
- Stage 0 / Sprint 0.2 — UI Shell Foundation
- Stage 0 / Sprint 0.3 — Migration and PWA Placeholder Closure

Current:
- Stage 1 / Sprint 1.1 — Auth + Admin Seed

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
6. Run the Flask app.

Commands:

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
flask seed-admin
python run.py

Open:

http://127.0.0.1:5000/
http://127.0.0.1:5000/health

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
- Tests
- Sprint documentation

Not implemented yet:
- RBAC
- Roles
- Permissions
- Audit
- Patients
- Appointments
- Visits
- Clinical modules
- Settings UI
- AI layer
