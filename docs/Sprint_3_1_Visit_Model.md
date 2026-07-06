# Stage 3 — Sprint 3.1 Visit Model & Migration

## Goal

Create the Visit database foundation.

## Scope

- Visit model
- VisitAuditLog model
- Visit belongs to Patient
- Structured clinical note fields
- Visit type/status rules
- Complete Visit service
- Reopen Visit service
- Confirmation required for complete/reopen
- Doctor/Admin required for reopen
- Minimal audit for complete/reopen
- Tests
- Migration
- Documentation

## Out of Scope

- Visit UI
- New Visit button activation
- Journey model
- Link Visit to Journey
- Timeline
- OITI sheet
- Specialized Visit templates
- Prescription
- Investigations
- Ultrasound
- Appointment integration

## Database Impact

Create:

- visits
- visit_audit_logs

## Visit Types

- obs
- gyn
- infertility
- oiti
- iui
- procedure
- general

## Visit Status

- open
- completed
- incomplete

## Visit Fields

- id
- uuid
- patient_id
- visit_type
- status
- visit_date
- started_at
- completed_at
- reopened_at
- chief_complaint
- history
- examination
- assessment
- plan
- follow_up_date
- is_locked
- completed_by_user_id
- reopened_by_user_id
- created_at
- updated_at

## VisitAuditLog Fields

- id
- visit_id
- patient_id
- actor_user_id
- action
- from_status
- to_status
- message
- created_at

## Rules

- Visit must belong to Patient.
- Visit can exist without Journey in Sprint 3.1.
- No journey_id column yet.
- Journey linking starts in Sprint 3.3.
- Visit type is required.
- Visit status defaults to open.
- Completed Visit is locked.
- Completed Visit cannot be edited until reopened.
- Complete Visit requires confirmation.
- Reopen Visit requires confirmation.
- Reopen Visit is Doctor/Admin only.
- No edit reason is required now.
- Complete/reopen creates VisitAuditLog.

## Acceptance Criteria

- Visit model exists.
- VisitAuditLog model exists.
- Visit belongs to Patient.
- Visit has UUID.
- Visit has type/status.
- Visit has structured note fields.
- Visit can be completed with confirmation.
- Completed Visit is locked.
- Completed Visit creates audit log.
- Visit can be reopened by Doctor/Admin with confirmation.
- Reopen creates audit log.
- Reception cannot reopen Visit.
- Visit can exist without Journey.
- Tests pass.
- Migration head clean.
- No UI added.
