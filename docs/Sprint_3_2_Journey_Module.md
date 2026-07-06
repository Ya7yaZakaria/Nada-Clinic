# Stage 3 — Sprint 3.2 Journey Module

## Goal

Create optional clinical context for patient care.

## Scope

- Journey model
- Journey service
- Journey forms
- Journey routes
- Journey templates
- Patient owns journeys
- Active/closed status
- Outcome by journey type
- Lost to follow-up outcome for all types
- Flexible end date: YYYY, YYYY-MM, or YYYY-MM-DD
- Journey close/reopen workflow
- Tests
- Migration
- Documentation

## Out of Scope

- Visit linkage
- Timeline
- Partner
- Pregnancy details
- Infertility cycle details
- OITI sheet
- Ultrasound
- Investigations
- Appointment integration

## Rules

- Journey belongs to Patient.
- Patient can have multiple journeys.
- Only one active journey of the same type.
- Multiple closed journeys allowed.
- Different journey types can be active simultaneously.
- Journey may exist without visits.
- Closing journey requires outcome and end date.
- End date accepts year only, year-month, or full date.
- Outcome note is optional for any outcome.
- Reopening journey clears end date, precision, outcome, and outcome note.
