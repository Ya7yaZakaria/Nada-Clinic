# Stage 1 — Sprint 1.1 Auth + Admin Seed

## Goal

Users can login/logout securely, and the first admin seed user can be created locally.

## Scope

- User model
- Password hashing
- Email or phone login
- Login route
- Logout route
- Protected dashboard
- Admin seed command
- Login template
- Auth tests

## Out of Scope

- RBAC
- Roles
- Permissions
- Audit
- Patients
- Appointments
- Visits
- Clinical modules
- Settings UI

## Files Created

- app/models/user.py
- app/routes/auth.py
- app/forms/auth_forms.py
- app/services/auth_service.py
- app/commands.py
- app/templates/auth/login.html
- tests/test_auth.py
- migrations/versions/*_add_users.py

## Files Modified

- app/__init__.py
- app/extensions.py
- app/models/__init__.py
- app/routes/main.py
- app/templates/base.html
- app/templates/index.html
- tests/test_health.py
- tests/test_pwa_placeholders.py
- .env.example
- README.md
- CHANGELOG.md

## Database Impact

Creates the users table.

## Migration Impact

A new Alembic migration is required.

## Acceptance Criteria

- User can login by email.
- User can login by phone if phone exists.
- Password is hashed.
- Anonymous users are redirected to login.
- Logged-in users can access dashboard.
- User can logout.
- Admin seed command creates first local admin seed user.
- Health endpoint remains public.
- Tests pass.
