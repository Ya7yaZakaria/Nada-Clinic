# Stages 00 02 Foundation Patients

Historical sprint/stage source material consolidated verbatim. It is retained for traceability and does not override current code.

## Included legacy sources

- `Sprint_0_1_Foundation.md`
- `Sprint_0_2_UI_Shell_Foundation.md`
- `Sprint_0_3_Migration_PWA_Closure.md`
- `Sprint_1_1_Auth.md`
- `Sprint_1_2_RBAC.md`
- `Sprint_1_3_Settings.md`
- `Sprint_2_1_Patient_Model.md`
- `Sprint_2_2_Patient_CRUD.md`
- `Sprint_2_3_Patient_Search.md`
- `Sprint_2_4_Patient_Workspace.md`

---

## Legacy source: `Sprint_0_1_Foundation.md`

# Sprint 0.1 — Flask Project Foundation

## Goal

Create a clean Flask foundation for Nada Clinic System.

## Scope

- App factory
- Config
- Extensions
- Main route
- Health route
- Base templates
- Static assets
- Tests
- Documentation baseline

## Out of Scope

- Auth
- RBAC
- Patients
- Visits
- Appointments
- Clinical modules
- AI layer

## Acceptance Criteria

- App starts.
- `/` renders.
- `/health` returns OK.
- Tests pass.
- GitHub contains foundation files.

---

## Legacy source: `Sprint_0_2_UI_Shell_Foundation.md`

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

---

## Legacy source: `Sprint_0_3_Migration_PWA_Closure.md`

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

---

## Legacy source: `Sprint_1_1_Auth.md`

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

---

## Legacy source: `Sprint_1_2_RBAC.md`

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

---

## Legacy source: `Sprint_1_3_Settings.md`

# Stage 1 — Sprint 1.3 Settings Foundation

## Goal

Create useful clinic/system settings foundation for personalization and organization.

## Scope

- Setting model
- Settings service
- Admin settings page
- Grouped settings
- Settings seed command
- Settings tests

## Out of Scope

- Audit
- Patient CRUD
- Appointment CRUD
- Visit CRUD
- Clinical modules
- AI features
- Storing secrets or API keys in settings

## Files Created

- app/models/setting.py
- app/services/settings_service.py
- app/forms/settings_forms.py
- app/templates/admin/settings.html
- tests/test_settings.py
- migrations/versions/*_add_settings.py

## Files Modified

- app/routes/admin.py
- app/models/__init__.py
- app/forms/__init__.py
- app/templates/base.html
- app/commands.py
- README.md
- CHANGELOG.md

## Database Impact

Creates the settings table.

## Settings Groups

- clinic
- localization
- appearance
- workflow
- printing
- security
- system

## Routes

- GET /admin/settings
- POST /admin/settings

## Services

- SettingsService.get()
- SettingsService.set()
- SettingsService.get_group()
- SettingsService.get_public_settings()
- SettingsService.seed_defaults()

## Acceptance Criteria

- Settings table exists.
- Default settings exist.
- Admin can manage settings.
- Non-admin is blocked.
- Settings can be updated.
- Public settings can be read safely.
- Tests pass.

---

## Legacy source: `Sprint_2_1_Patient_Model.md`

# Stage 2 — Sprint 2.1 Patient Model & Migration

## Goal

Create the patient database foundation.

## Scope

- Patient table
- UUID internal ID
- Integer MRN
- Padded MRN display helper
- Arabic and English names
- Search name
- Demographics
- Address
- Phone
- DOB/manual age logic
- Virgin checkbox
- Patient service
- Tests
- Migration
- Documentation

## Out of Scope

- Patient CRUD UI
- Patient search UI
- Patient workspace UI
- Appointments
- Visits
- Clinical notes
- Audit table
- Partner
- National ID

## Database Impact

Create `patients` table.

## Patient Fields

- id
- uuid
- medical_file_number
- name_ar
- name_en
- search_name
- gender
- date_of_birth
- age_years_at_registration
- age_recorded_at
- marital_status
- is_virgin
- occupation
- phone_primary
- phone_secondary
- email
- governorate
- city
- street
- is_active
- created_at
- updated_at

## Rules

Required:

- name_ar
- name_en
- phone_primary
- date_of_birth OR age_years_at_registration

Defaults:

- gender = female
- marital_status = unknown
- is_virgin = False
- is_active = True

MRN:

- Stored as integer
- Unique
- Auto-generated
- Displayed as 6 digits
- Example: 1 -> 000001

Phone:

- Required
- Duplicate allowed
- Duplicate can be detected for warning

National ID:

- Not included in Stage 2

MRN edit:

- Admin-only later in CRUD
- No audit table in Sprint 2.1
- No reason required
- Warning before change in UI later

## Services

- PatientService.generate_next_mrn()
- PatientService.format_mrn()
- PatientService.build_search_name()
- PatientService.create_patient()
- PatientService.update_patient()
- PatientService.change_medical_file_number()
- PatientService.calculate_display_age()
- PatientService.get_display_name()
- PatientService.get_full_address()
- PatientService.find_duplicate_phone_patients()

## Acceptance Criteria

- Patient table exists.
- Patient has UUID.
- MRN is integer.
- MRN displays as 6-digit padded number.
- Arabic and English names are required.
- Search name supports both languages.
- Phone is required but not unique.
- Duplicate phone warning support exists.
- DOB/manual age rule works.
- Patient age display works.
- Address has governorate/city/street only.
- Virgin check exists.
- No national_id.
- No audit table.
- Tests pass.
- Migration head clean.

---

## Legacy source: `Sprint_2_2_Patient_CRUD.md`

# Stage 2 — Sprint 2.2 Patient CRUD

## Goal

Create, edit, and view patient identity records.

## Scope

- Patients blueprint
- Patient form
- MRN change form
- Patient list
- New patient
- Create patient
- Patient detail/workspace shell
- Edit patient
- Admin-only MRN edit with warning
- Duplicate phone warning
- Tests
- Documentation

## Out of Scope

- Patient live search
- Appointment implementation
- Visit implementation
- Clinical notes
- Timeline implementation
- Documents
- Partner

## Routes

- GET /patients/
- GET /patients/new
- POST /patients/new
- GET /patients/<uuid>
- GET /patients/<uuid>/edit
- POST /patients/<uuid>/edit
- POST /patients/<uuid>/mrn
- POST /patients/<uuid>/deactivate

## Permissions

- patients.basic.view
- patients.basic.create
- admin.access for MRN edit and deactivate

## Templates

- patients/index.html
- patients/new.html
- patients/detail.html
- patients/edit.html
- patients/_form.html

## Acceptance Criteria

- Anonymous user is redirected to login.
- Doctor can view patients.
- Reception can create patients.
- Patient can be created.
- Patient can be edited.
- Duplicate phone is allowed with warning.
- Doctor/Reception cannot edit MRN.
- Admin can edit MRN after warning confirmation.
- Patient workspace shell opens.
- Header shows MRN/name/age/phone/address.
- Quick actions show New Visit / Visits / Edit.
- No real Visit implementation added.

---

## Legacy source: `Sprint_2_3_Patient_Search.md`

# Stage 2 — Sprint 2.3 Patient Search

## Goal

Create fast patient search by Arabic name, English name, MRN, and phone.

## Scope

- PatientService search helpers
- Patient search route
- HTMX search input on patients index
- Search results partial
- Patient card partial
- Recent patients when search is empty
- Search tests
- Clean SQLAlchemy legacy Query.get warnings in patient CRUD tests
- Documentation

## Out of Scope

- Global topbar search
- Advanced filters
- Pagination
- Appointment implementation
- Visit implementation
- Clinical notes
- Timeline implementation

## Routes

- GET /patients/search

## Search Fields

- medical_file_number
- formatted/padded MRN input
- name_ar
- name_en
- search_name
- phone_primary
- phone_secondary

## HTMX

- hx-get="/patients/search"
- hx-trigger="keyup changed delay:250ms, search"
- hx-target="#patient-search-results"
- hx-swap="innerHTML"

## Templates

- patients/_search_results.html
- patients/_patient_card.html
- patients/index.html updated with search input

## Acceptance Criteria

- Anonymous user is redirected to login.
- Doctor can search patients.
- Search by Arabic name works.
- Search by English name works.
- Search by integer MRN works.
- Search by padded MRN works.
- Search by phone works.
- Duplicate phone search can return multiple patients.
- Empty search returns recent patients.
- Patient index contains HTMX live search input.
- Tests pass without SQLAlchemy LegacyAPIWarning from patient CRUD tests.

---

## Legacy source: `Sprint_2_4_Patient_Workspace.md`

# Stage 2 — Sprint 2.4 Patient Workspace v1

## Goal

Refine the Patient Workspace as the fast patient-centered entry point.

## Scope

- Improved patient workspace header
- MRN/name/age/phone/address display
- Name display based on system language
- Virgin badge/check display
- Patient identity card
- Clinical Snapshot placeholder
- Recent Visits placeholder
- Quick Actions placeholder
- Workspace tests
- Documentation

## Out of Scope

- Real Visit implementation
- Clinical notes
- Timeline implementation
- Appointment integration
- Investigations
- Documents
- Partner module

## Workspace Route

- GET /patients/<uuid>

## Header

- MRN
- Display name based on localization.language
- Age
- Phone
- Address

## Quick Actions

- New Visit placeholder
- Visits placeholder
- Edit active link

## Acceptance Criteria

- Patient Workspace opens quickly.
- Header shows MRN/name/age/phone/address.
- Name follows system language setting.
- Virgin check is visible.
- Clinical Snapshot placeholder exists.
- Recent Visits placeholder exists.
- Quick actions show New Visit / Visits / Edit.
- New Visit and Visits are disabled placeholders.
- No real Visit implementation added.
- Tests pass.
- Migration head remains clean.

---
