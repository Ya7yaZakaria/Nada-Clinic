# Nada Clinic System

Nada Clinic System is a doctor-first, patient-centered clinic operating system for OB/GYN workflows.

## Current Stage

Sprint 0.1 — Flask Project Foundation.

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

```powershell

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
Open:

http://127.0.0.1:5000/
http://127.0.0.1:5000/health
Tests
python -m pytest
Flask CLI
$env:FLASK_APP="app"
flask routes
Project Philosophy
Doctor-first
Patient-centered
Fast
Minimal clicks
Timeline-driven
AI-ready
Mobile/iPad friendly
Current Scope

Foundation only.

Clinical modules, authentication, RBAC, patients, visits, appointments, prescriptions, investigations, documents, ultrasound, surgery, finance, reports, and AI layer will be added in later sprint
