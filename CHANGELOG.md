# Changelog

## 2026-07-06 — Stage 1 / Sprint 1.2 Multi-role RBAC

### Added

- Role model.
- Permission model.
- User-role association table.
- Role-permission association table.
- Multi-role user support.
- RBAC service.
- Permission decorator.
- 403 access denied page.
- Admin placeholder route.
- Clinical placeholder route for RBAC testing only.
- Reception placeholder route for RBAC testing only.
- Role/permission seed command.
- RBAC tests.
- Sprint 1.2 documentation.

### Not Added Yet

- Audit.
- Settings UI.
- Patient CRUD.
- Appointment CRUD.
- Visit CRUD.
- Real clinical modules.
- AI features.
# Changelog

## 2026-07-06 — Stage 1 / Sprint 1.1 Auth + Admin Seed

### Added

- User model.
- Password hashing.
- Email or phone login.
- Login route.
- Logout route.
- Protected dashboard.
- Admin seed command.
- Login template.
- Auth service.
- Login form.
- Auth tests.
- User migration.
- Sprint 1.1 documentation.

### Not Added Yet

- RBAC.
- Roles.
- Permissions.
- Audit.
- Patients.
- Appointments.
- Visits.
- Clinical modules.
- Settings UI.
- AI features.

## 2026-07-06 — Stage 0 / Sprint 0.3 Migration and PWA Placeholder Closure

### Added

- Flask-Migrate / Alembic migration structure.
- PWA placeholder manifest.
- PWA placeholder service worker.
- Base template manifest reference.
- Base template service worker registration.
- PWA placeholder tests.
- Sprint 0.3 documentation.

## 2026-07-06 — Stage 0 / Sprint 0.2 UI Shell Foundation

### Added

- Clinic OS sidebar shell.
- Topbar layout.
- Mobile sidebar behavior using Alpine.js.
- Placeholder navigation for Dashboard, Today Clinic, Patients, Appointments, Visits, Investigations, Reports, and Settings.
- Dashboard placeholder cards for future clinic modules.
- HTMX-ready main content area.
- UI shell tests.
- Sprint 0.2 documentation.

## 2026-07-06 — Stage 0 / Sprint 0.1 Foundation

### Added

- Flask app factory.
- Configuration system.
- Extension registry.
- SQLAlchemy setup.
- Flask-Migrate setup.
- Flask-Login setup.
- CSRF setup.
- Main blueprint.
- `/` foundation page.
- `/health` endpoint.
- Bootstrap 5 base template.
- HTMX script.
- Alpine.js script.
- Basic static CSS and JS.
- Basic 404 and 500 templates.
- Initial pytest health tests.
- README baseline.
- `.env.example`.
- `.gitignore`.

