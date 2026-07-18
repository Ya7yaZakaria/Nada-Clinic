
# P2.4A Development Role Preview Freeze Review

Date: 2026-07-18

## Goal

Provide a development-only, system-wide role preview using the existing
authenticated account without modifying database roles.

## Scope Completed

- Session-based effective role preview.
- Admin, Doctor, and Reception preview roles.
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
- `tests/test_dev_role_preview.py`
- `docs/P2_4A_DEVELOPMENT_ROLE_PREVIEW_FREEZE.md`

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
- `docs/AGENT_MISTAKES.md`

## Database Impact

None.

## Migration Impact

None.

## Routes

- `POST /development/role-preview`
- `POST /development/role-preview/clear`

## Permissions and Security

- Existing permission matrix remains the source of role permissions.
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
