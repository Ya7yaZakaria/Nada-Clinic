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
