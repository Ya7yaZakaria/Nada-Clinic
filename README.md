# Nada Clinic System

Nada Clinic is a Flask-based clinic operating system centered on patient, appointment, visit, medication, investigation, document, ultrasound, surgery, partner, finance, printing, and settings workflows.

## Current development mode

The application is in personal-trial/refinement mode after the previously completed stage sequence. Current work should be driven by fresh repository inspection and real workflow evidence rather than old sprint plans.

## Stack

- Python / Flask
- SQLAlchemy
- Alembic / Flask-Migrate
- Flask-Login
- Flask-WTF / CSRF
- Jinja / Bootstrap
- HTMX and project JavaScript/CSS
- pytest

## Main project areas

Current source contains dedicated models, services, routes/forms/templates for patients, appointments/Today Clinic, visits/journeys, medications/prescriptions, investigations, documents, ultrasound, surgery, partner workflows, finance, printing, settings, authentication/RBAC, and development role preview.

See `docs/ARCHITECTURE.md` for the generated structural map.

## Run locally

From the repository root with the virtual environment active:

```powershell
python run.py
```

Useful Flask CLI inspection:

```powershell
$env:FLASK_APP = "app"
flask routes
flask db current
flask db heads
```

Do not run destructive migration/database operations merely to check the project.

## Tests

Current verified evidence supplied on 2026-08-09:

```text
544 tests collected in 3.08s
544 passed in 203.31s (0:03:23)
```

Focused development:

```powershell
python -m pytest tests/<affected-domain> -q
```

Daily broad regression when slow/migration coverage is unrelated:

```powershell
python -m pytest -m "not slow and not migration" -q
```

Full checkpoint suite:

```powershell
python -m pytest -q
```

See `docs/TESTING.md` for the current test structure and commands.

## Documentation

- `AGENTS.md` — authoritative guarded implementation workflow.
- `MEMORY.md` — concise current project memory/handoff.
- `CHANGELOG.md` — historical changes.
- `docs/ARCHITECTURE.md` — current structural map.
- `docs/TESTING.md` — test architecture, tiers, and performance rules.
- `docs/OPERATIONS.md` — local workflow and evidence rules.
- `docs/ROADMAP.md` — current future-work priorities.
- `docs/AGENT_LESSONS.md` — retained implementation lessons.
- `docs/DEVELOPMENT_ROLE_PREVIEW.md` — development-role-preview evidence.
- `docs/PERSONAL_TRIAL.md` — personal-trial/handoff history.
- `docs/history/` — consolidated historical sprint/stage source documents.

Historical docs are retained for traceability but do not override current source, `AGENTS.md`, or fresh runtime evidence.

## Safety

- Never commit `.env` or secrets.
- Do not treat the real database as a disposable verification database.
- Do not weaken tests to force a pass.
- Do not claim runtime, migration, or visual verification without corresponding evidence.
