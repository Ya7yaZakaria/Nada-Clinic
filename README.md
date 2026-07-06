# Nada Clinic System

Nada Clinic System is a doctor-first, patient-centered clinic operating system for OB/GYN workflows.

## Current Stage

Stage 0 — Project Preparation

Completed:
- Sprint 0.1 — Flask Project Foundation
- Sprint 0.2 — UI Shell Foundation
- Sprint 0.3 — Migration and PWA Placeholder Closure

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
3. Run the Flask app.

Commands:

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
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

## Project Philosophy

- Doctor-first
- Patient-centered
- Fast
- Minimal clicks
- Timeline-driven
- AI-ready
- Mobile/iPad friendly

## Current Scope

Stage 0 foundation only.

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
- Tests
- Sprint documentation

Not implemented yet:
- Auth
- RBAC
- Audit
- Patients
- Appointments
- Visits
- Clinical modules
- AI layer
