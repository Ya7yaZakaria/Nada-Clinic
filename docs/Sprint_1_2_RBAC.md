# Stage 1 — Sprint 1.2 Multi-role RBAC

## Goal

Separate Admin, Doctor, and Reception access, with support for users having multiple roles.

## Scope

- Role model
- Permission model
- UserRole table
- RolePermission table
- RBAC helper
- Permission decorator
- Access denied page
- Role/permission seed command
- RBAC tests

## Out of Scope

- Audit
- Settings UI
- Patient CRUD
- Appointment CRUD
- Visit CRUD
- Real clinical modules

## Files Created

- app/models/role.py
- app/models/permission.py
- app/services/rbac_service.py
- app/routes/admin.py
- app/templates/errors/403.html
- app/templates/admin/index.html
- app/templates/placeholders/clinical.html
- app/templates/placeholders/reception.html
- tests/test_rbac.py
- migrations/versions/*_add_roles_permissions.py

## Files Modified

- app/models/user.py
- app/models/__init__.py
- app/commands.py
- app/__init__.py
- app/routes/main.py
- app/templates/base.html
- tests/test_health.py
- tests/test_pwa_placeholders.py
- README.md
- CHANGELOG.md

## Database Impact

Creates:

- roles
- permissions
- user_roles
- role_permissions

## Permission Matrix

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

## Role Matrix

Admin:
- all permissions

Doctor:
- dashboard.view
- patients.basic.view
- appointments.view
- clinical.view
- clinical.note.view
- clinical.note.write

Reception:
- dashboard.view
- patients.basic.view
- patients.basic.create
- appointments.view
- appointments.manage

## Acceptance Criteria

- Roles exist.
- Permissions exist.
- User can have multiple roles.
- Admin has all permissions.
- Doctor and Reception are separated correctly.
- Reception cannot access clinical notes placeholder.
- Doctor can access clinical placeholder.
- 403 page exists.
- Tests pass.
