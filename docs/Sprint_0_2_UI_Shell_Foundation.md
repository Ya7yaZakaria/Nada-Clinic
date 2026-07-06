# Stage 0 — Sprint 0.2 UI Shell Foundation

## Goal

Create the first Clinic OS visual shell without implementing clinical business modules.

## Scope

- Sidebar shell
- Topbar shell
- Mobile sidebar behavior
- Main content area
- Placeholder navigation
- Dashboard placeholder cards
- HTMX-ready content area
- Alpine.js sidebar state
- UI shell tests

## Out of Scope

- Authentication
- RBAC
- Audit
- Patient CRUD
- Appointment CRUD
- Visit CRUD
- Database models
- Migrations

## Files Modified

- app/templates/base.html
- app/templates/index.html
- app/static/css/app.css
- app/static/js/app.js
- tests/test_health.py
- CHANGELOG.md

## Files Created

- docs/Sprint_0_2_UI_Shell_Foundation.md

## Acceptance Criteria

- `/` renders the Clinic OS shell.
- `/health` still returns OK.
- Sidebar contains placeholder navigation.
- Mobile menu uses Alpine.js state.
- Tests pass.
- No clinical model or auth code is added.
