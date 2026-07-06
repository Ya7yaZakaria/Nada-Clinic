# Stage 0 — Sprint 0.3 Migration and PWA Placeholder Closure

## Goal

Close the remaining Stage 0 preparation gaps before moving to feature work.

## Scope

- Initialize Flask-Migrate / Alembic structure.
- Add PWA placeholder files.
- Reference manifest from the base template.
- Register placeholder service worker.
- Add tests for PWA placeholder presence.
- Update Stage 0 documentation.

## Out of Scope

- Authentication
- RBAC
- Audit
- Patient CRUD
- Appointment CRUD
- Visit CRUD
- Clinical database models
- Real offline caching
- Production PWA behavior

## Files Created

- migrations/
- app/static/manifest.json
- app/static/service-worker.js
- tests/test_pwa_placeholders.py
- docs/Sprint_0_3_Migration_PWA_Closure.md

## Files Modified

- app/templates/base.html
- CHANGELOG.md
- README.md

## Acceptance Criteria

- Alembic migration structure exists.
- `migrations/env.py` exists.
- `/` still renders.
- `/health` still returns OK.
- PWA placeholder files exist.
- Base template references manifest and service worker.
- Tests pass.
- No clinical feature code is added.
