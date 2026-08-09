# P2.4A Development Role Preview Freeze Review

Date: 2026-07-18

## Goal

Provide a development-only, system-wide role preview using the existing
authenticated account without modifying database roles.

## Scope Completed

- Session-based effective role preview.
- Database-backed role selector, including future stored roles.
- Development configuration guard.
- Email allowlist.
- Central RBAC integration.
- User helper integration.
- Route and template protection.
- Dashboard permission-aware query behavior.
- Desktop application-shell selector.
- Persistent preview banner.
- Reset to actual roles.
- Logout cleanup.
- Automated tests.

## Out of Scope Confirmed

- New users.
- Database role mutation.
- Permission schema changes.
- Database migration.
- Production role switching.
- Demo data.
- Stage 13 Reports.

## Files Created

- `app/routes/development.py`
- `app/services/development_role_preview_service.py`
- `tests/auth_rbac/test_dev_role_preview.py`
- `docs/DEVELOPMENT_ROLE_PREVIEW.md`

## Files Modified

- `app/__init__.py`
- `app/config.py`
- `app/models/user.py`
- `app/routes/auth.py`
- `app/services/rbac_service.py`
- `app/static/css/app.css`
- `app/templates/base.html`
- `README.md`
- `CHANGELOG.md`
- `MEMORY.md`
- `docs/AGENT_LESSONS.md`

## Database Impact

None.

## Migration Impact

None.

## Routes

- `POST /development/role-preview`
- `POST /development/role-preview/clear`

## Permissions and Security

- Preview permissions come from the selected database `Role.permissions` relationship.
- The effective preview role is applied only during an active request.
- The actual user roles remain stored unchanged in the database.
- Non-allowlisted users receive 404 from preview routes.
- Unsupported role names are rejected.
- Logout clears preview session state.
- Production remains disabled by default.

## Tests

- Feature tests: 7 passed.
- Related RBAC, Auth, shell, and dashboard tests: 32 passed.
- Full regression: 478 passed.

## Manual Testing

Accepted:

- Reception preview.
- Doctor preview.
- Admin preview.
- Return to actual roles.
- Logout reset.
- System-wide navigation and route restrictions.
- Application startup.
- Development route registration.

## Freeze Review

- Models reviewed: no schema change.
- Migrations reviewed: none created.
- Routes reviewed.
- Services reviewed.
- Templates reviewed.
- Permissions reviewed.
- RBAC reviewed.
- Security reviewed.
- Tests reviewed.
- Documentation updated.
- No migration drift introduced.
- No unrelated feature changes identified from the planned scope.

## Status

P2.4A is ready for final Git review and manual commit.

## 2026-08-09 — Dynamic role preview extension

The development selector now reads available roles from the `roles` table instead
of a hard-coded role-name list. Preview authorization still requires the existing
development enable flag and email allowlist.

While a preview is active, permission checks use the selected database
`Role.permissions` relationship. Therefore, a future role becomes available in
the selector and uses its stored permissions without adding that role name to
the preview service or to a separate preview permission matrix.

No user role is mutated, production remains disabled by default, and no database
migration is required for this extension.
