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
