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
