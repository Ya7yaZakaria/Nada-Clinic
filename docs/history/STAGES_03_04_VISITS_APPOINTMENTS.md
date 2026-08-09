# Stages 03 04 Visits Appointments

Historical sprint/stage source material consolidated verbatim. It is retained for traceability and does not override current code.

## Included legacy sources

- `Sprint_3B_Freeze_Review.md`
- `Sprint_3_1_Visit_Model.md`
- `Sprint_3_2_Journey_Module.md`
- `Sprint_3_3_Link_Visit_Journey.md`
- `Sprint_3_4_Timeline_Foundation.md`
- `Sprint_4_1_Appointment_Model.md`
- `Sprint_4_2_Appointment_Booking_Calendar.md`
- `Sprint_4_3_Arrival_Waiting_Queue.md`
- `Sprint_4_4_Todays_Clinic.md`
- `Sprint_4_5_Previous_Days_Clinic.md`
- `Sprint_4_6_Stage_4_Freeze_Review.md`

---

## Legacy source: `Sprint_3B_Freeze_Review.md`

# Sprint 3B Freeze Review

## Status

Ready to commit.

## Scope

Sprint 3B includes:

- Cancel and Reschedule HTMX actions.
- Close Day HTMX workflow.
- Add Emergency HTMX workflow.
- Quick Appointment Edit HTMX workflow.
- Final Duration-field cleanup.
- Close Day current-date protection.

## Sprint 3B1 — Cancel and Reschedule

Confirmed:

- HTMX modals and inline validation.
- Normal POST fallbacks.
- `appointments.manage` permission.
- Flask-WTF CSRF protection.
- Finance cancellation behavior.
- Active Appointment and Visit-start guards.

## Sprint 3B2 — Close Day

Confirmed:

- HTMX preview and confirmation.
- Booked appointments convert to No Show.
- Repeat submission safety.
- Dynamic Today Clinic refresh.
- Malformed date values return 404.
- Past and future clinic dates return 409.
- Direct blocked POST requests do not mutate appointments.
- Close Day is limited to the current clinic date.

## Sprint 3B3 — Add Emergency

Confirmed:

- HTMX modal and patient search.
- Inline validation.
- Same-day emergency appointment creation.
- Immediate Waiting queue entry.
- Dynamic queue and counter refresh.
- RBAC and CSRF protection.

## Sprint 3B4 — Quick Appointment Edit

Confirmed fields:

- Appointment time.
- Appointment type.
- Notes.
- Fee.
- Paid amount.
- Payment method.

Duration is intentionally absent from:

- `AppointmentForm`
- `AppointmentQuickEditForm`
- Appointment booking UI
- Quick Edit UI

The existing Appointment database `duration_minutes` column remains unchanged.

Historical duration values remain preserved.

The patient-workspace booking route no longer reads
`form.duration_minutes`; the service default of `None` is used.

## Files Changed

- `app/forms/appointment_forms.py`
- `app/routes/patients.py`
- `app/routes/today_clinic.py`
- `tests/test_today_clinic_htmx_actions.py`
- `MEMORY.md`
- `CHANGELOG.md`
- `docs/AGENT_MISTAKES.md`
- `docs/Sprint_3B_Freeze_Review.md`

## Database and Migration

- No model change.
- No migration added.
- Migration head: `20260719_0070`.
- Migration current: `20260719_0070`.
- `flask db check` still detects pre-existing drift:
  - Drug dictionary unique indexes.
  - Surgery case indexes.
- This drift is separate from Sprint 3B.

## Verification

- Patient-workspace regression test: 1 passed in 1.64s.
- Appointment CRUD tests: 5 passed in 3.80s.
- Focused Today Clinic tests: 43 passed in 25.90s.
- Full regression: 549 passed in 266.92s.
- `git diff --check`: no whitespace errors.
- Manual Today Clinic UI verification was previously accepted.

## Starting Commit

`9b3c122`

## Verdict

Ready to commit.

No Sprint 3B model or migration changes are required.

---

## Legacy source: `Sprint_3_1_Visit_Model.md`

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

---

## Legacy source: `Sprint_3_2_Journey_Module.md`

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

---

## Legacy source: `Sprint_3_3_Link_Visit_Journey.md`

# Stage 3 — Sprint 3.3 Link Visit to Journey

## Goal

Link Visit to optional Journey while preserving standalone visits.

## Scope

- Add nullable journey_id to visits
- Visit can remain standalone
- Visit can link to Journey
- Visit can link to closed Journey
- Cross-patient Journey link blocked
- Visit UI foundation
- Patient Workspace active journeys and recent visits
- Warning for standalone/unassigned Visit
- Tests
- Migration
- Documentation

## Out of Scope

- Timeline
- Visit templates
- OITI sheet
- Pregnancy details
- Ultrasound
- Investigations
- Prescription
- Appointment integration

## Rules

- Visit must belong to Patient.
- Journey is optional.
- Journey must belong to same Patient.
- Closed Journey can be linked.
- Unassigned Visit shows warning.
- Reception cannot create/edit clinical Visit.

---

## Legacy source: `Sprint_3_4_Timeline_Foundation.md`

# Stage 3 — Sprint 3.4 Timeline Foundation

## Goal

Show the patient story from existing clinical records.

## Scope

- Generated timeline only
- No timeline table
- Timeline service
- Patient Workspace timeline section
- Journey started events
- Journey closed events
- Visit events
- Visit completed events
- Visit reopened events
- Unassigned Visit marker
- Tests
- Documentation

## Out of Scope

- Manual timeline events
- Timeline filters
- Timeline table
- Prescription events
- Investigation events
- Ultrasound events
- Appointment events
- Surgery events

## Rules

- Timeline is generated at runtime.
- Timeline does not duplicate data.
- Timeline uses Journeys and Visits.
- Newest events appear first.
- No separate Timeline model or table.

## Acceptance Criteria

- Timeline service exists.
- Patient Workspace shows Timeline section.
- Journey events appear.
- Visit events appear.
- Completed/reopened Visit events appear.
- Unassigned Visit is marked.
- No Timeline table exists.
- Tests pass.
- Migration head clean.

---

## Legacy source: `Sprint_4_1_Appointment_Model.md`

# Sprint 4.1 — Appointment Model & Migration

## Goal
Create Appointment database foundation for Stage 4 — Appointment & Today’s Clinic.

## Scope
- Appointment model
- Appointment service
- Appointment type/status/source validation
- Patient relationship
- Status workflow timestamps
- Emergency unscheduled appointment support
- End-of-day no-show conversion
- Counters for clinic day
- Tests
- Migration

## Out of Scope
- Routes
- UI
- Calendar
- Today’s Clinic dashboard
- Billing
- Procedure add-ons
- Visit auto-creation

## Important Decisions
- Patient remains the root entity.
- Appointment does not automatically create Visit.
- Today’s Clinic is generated from appointments by date.
- Procedure is not an appointment type.
- Arrived means Waiting.
- No in_consultation status.
- No-show is created by end-of-day conversion.
- Total Booked Today counts all appointments for the selected date regardless of status.

## Appointment Types
- new_consultation
- follow_up
- emergency

## Appointment Statuses
- booked
- arrived
- completed
- cancelled
- rescheduled
- no_show

## Appointment Sources
- phone
- whatsapp
- clinic
- emergency_unscheduled

## Files Created
- app/models/appointment.py
- app/services/appointment_service.py
- tests/test_appointment_model.py
- docs/Sprint_4_1_Appointment_Model.md

## Files Modified
- app/models/__init__.py
- README.md
- CHANGELOG.md

## Database Impact
Creates appointments table.

## Migration Impact
Alembic migration should be autogenerated.

## Verification Commands
```bash
flask db migrate -m "add appointments"
flask db upgrade
flask routes
python -m pytest
flask db heads
flask db current
git status
git diff --statAcceptance Criteria
Appointment model exists.
Appointment belongs to Patient.
Appointment type values fixed.
Procedure type rejected.
Status workflow works.
Emergency unscheduled support exists.
Appointment does not create Visit.
End-of-day no-show conversion exists.
Total Booked Today counter works.
Tests pass.
Migration head clean.

---

## Legacy source: `Sprint_4_2_Appointment_Booking_Calendar.md`

# Sprint 4.2 — Appointment Booking + Calendar View

## Goal
Reception can book appointments, and clinic users can view appointments on a useful calendar.

## Scope
- Appointment routes
- Appointment form
- Appointment booking page
- Appointment edit page
- Appointment detail page
- Appointment list by date
- Calendar month/week/day view
- Selected day appointments panel
- Patient appointment list
- Booking from Patient Workspace
- Tests
- Documentation

## Out of Scope
- Arrival/check-in workflow
- Cancel workflow
- Reschedule workflow routes
- Today’s Clinic dashboard
- Billing
- Procedures
- Notifications
- Online booking
- Drag/drop calendar

## Routes
- GET /appointments/calendar
- GET /appointments
- GET /appointments/new
- POST /appointments/new
- GET /appointments/<appointment_uuid>
- GET /appointments/<appointment_uuid>/edit
- POST /appointments/<appointment_uuid>/edit
- GET /patients/<patient_uuid>/appointments/new
- POST /patients/<patient_uuid>/appointments/new
- GET /patients/<patient_uuid>/appointments

## Permissions
- appointments.view
- appointments.manage

## Acceptance Criteria
- Booking page works.
- Calendar view works.
- Appointment can be booked for Patient.
- Appointment can be edited.
- Calendar shows appointment counts.
- Calendar includes all statuses in count.
- Patient appointment list works.
- Appointment does not create Visit.
- Tests pass.
- Migration head remains clean.

---

## Legacy source: `Sprint_4_3_Arrival_Waiting_Queue.md`

# Sprint 4.3 — Arrival / Waiting Queue

## Goal
Reception can check-in patients and manage non-clinical appointment workflow.

## Scope
- Mark appointment arrived
- Arrived means waiting
- Cancel appointment
- Reschedule appointment
- Emergency unscheduled appointment route
- Waiting queue service
- Tests
- Documentation

## Out of Scope
- Today’s Clinic dashboard
- Visit auto-creation
- Billing
- Procedure add-ons
- Multi-room queue
- Notifications

## Routes
- POST /appointments/<appointment_uuid>/arrive
- POST /appointments/<appointment_uuid>/cancel
- POST /appointments/<appointment_uuid>/reschedule
- GET /appointments/emergency/new
- POST /appointments/emergency/new

## Rules
- Arrived means Waiting.
- No in_consultation status.
- Reception can mark arrived.
- Reception can cancel/reschedule.
- Emergency unscheduled creates an arrived emergency appointment.
- Appointment still does not create Visit.
- Patient Workspace remains doctor-first.

## Acceptance Criteria
- Reception can check-in patient in one click.
- Arrived appointment appears in waiting queue.
- Emergency unscheduled workflow exists.
- Cancel/reschedule work.
- Appointment does not create Visit.
- Tests pass.
- Migration head remains clean.

---

## Legacy source: `Sprint_4_4_Todays_Clinic.md`

# Sprint 4.4 — Today’s Clinic Dashboard

## Goal
Doctor sees a live clinic list for the selected day.

## Scope
- Today’s Clinic dashboard
- Smart counters
- Full day appointment list
- Waiting list
- Patient preview
- Open Patient Workspace
- Start Visit action
- Active Journey badges
- Last Visit display
- Pending flags placeholder
- End-of-day close action
- Tests
- Documentation

## Rules
- Today’s Clinic does not create Visit automatically.
- Doctor opens Patient Workspace manually.
- Doctor starts Visit manually.
- Completed Visit can later mark Appointment completed.
- Pending flags are placeholders only.
- Today’s Clinic is a generated view, not a separate table.
- Today’s Clinic shows the selected day’s appointments only.
- Total Booked Today counts every appointment for that day regardless of status.
- Patients remain visible while status changes.
- End-of-day close converts remaining booked appointments to no_show.

## Routes
- GET /clinic/today
- GET /clinic/day/<clinic_date>
- POST /clinic/day/<clinic_date>/close
- POST /clinic/appointments/<appointment_uuid>/complete

## Services
- AppointmentService.get_today_clinic()
- AppointmentService.get_clinic_day()
- AppointmentService.get_counters_for_date()
- AppointmentService.get_waiting_queue()
- AppointmentService.get_booked_no_action()
- AppointmentService.get_completed_for_date()
- AppointmentService.get_cancelled_for_date()
- AppointmentService.get_rescheduled_for_date()
- AppointmentService.get_no_show_for_date()
- AppointmentService.close_clinic_day()

## Acceptance Criteria
- Doctor can open next patient quickly.
- Reception can see waiting flow.
- Counters work.
- Full day list works.
- Patients remain visible after status changes.
- Open Workspace is one click.
- New Visit is accessible.
- Appointment does not auto-create Visit.
- End-of-day no-show works.
- Tests pass.
- Migration head clean.

---

## Legacy source: `Sprint_4_5_Previous_Days_Clinic.md`

# Sprint 4.5 — Previous Days Clinic

## Goal
Review previous clinic days and unfinished work.

## Scope
- Previous days view
- Date navigation
- Past clinic day summary
- No-show list
- Arrived but not completed list
- Completed list
- Cancelled/rescheduled list
- Unfinished work placeholders
- Tests
- Documentation

## Rules
- Previous Days Clinic is generated from appointments.
- No separate clinic-day table.
- Useful for checking unfinished work.
- No automatic clinical editing.
- Previous Days is where old no-show history is reviewed.
- Today’s Clinic does not show previous days.

## Routes
- GET /clinic/previous
- GET /clinic/day/<clinic_date>

## Services
- AppointmentService.get_previous_clinic_days()
- AppointmentService.get_unfinished_for_date()
- AppointmentService.get_day_summary()

## Templates
- clinic/previous.html
- clinic/_previous_day_card.html
- clinic/past_day.html
- clinic/_past_day_summary.html

## Acceptance Criteria
- Previous clinic days can be reviewed.
- Unfinished work is visible.
- No-show history is visible.
- No separate clinic-day table.
- Tests pass.
- Migration head clean.

---

## Legacy source: `Sprint_4_6_Stage_4_Freeze_Review.md`

# Sprint 4.6 — Stage 4 Freeze Review

## Goal
Confirm Appointment & Today’s Clinic is stable before moving forward.

## Freeze Result
Stage 4 is frozen and accepted.

## Verified Date
2026-07-12

## Verified Commit
cb7b70c — feat(appointments): add previous clinic days review

## Verification Output
- Tests: 175 passed, 225 warnings
- Migration current: ecf98d78d1b4 (head)
- Migration heads: ecf98d78d1b4 (head)
- Git working tree: clean

## Freeze Checklist

### Appointment Foundation
- Appointment model exists.
- Appointment belongs to Patient.
- Appointment type values fixed:
  - new_consultation
  - follow_up
  - emergency
- Procedure is not an appointment type.
- Procedure remains deferred as a Visit add-on.
- Appointment types are billing-ready.

### Appointment Workflow
- Booking works.
- Calendar view works.
- Reschedule works.
- Cancel works.
- Arrived / waiting workflow works.
- Emergency unscheduled workflow works.
- End-of-day no-show conversion works.
- Status workflow works:
  - booked
  - arrived
  - completed
  - cancelled
  - rescheduled
  - no_show

### Today’s Clinic
- Today’s Clinic dashboard works.
- Today’s Clinic displays only selected current-day appointments.
- Total Booked Today counts all appointments for today regardless of status.
- Patients remain visible while status changes.
- Doctor can open Patient Workspace quickly.
- Doctor can start Visit manually.
- Appointment does not create Visit automatically.
- Completed appointment can be marked manually.

### Previous Days Clinic
- Previous clinic days can be reviewed.
- No-show history is visible.
- Arrived but not completed appointments are visible.
- Completed appointments are visible.
- Cancelled and rescheduled appointments are visible.
- Unfinished work placeholder exists.
- Previous Days Clinic is generated from appointments.
- No separate clinic-day table exists.

### Deferred / Not Implemented
- No billing implementation yet.
- No procedure add-on yet.
- No automatic clinical editing.
- No automatic Visit creation from Appointment.
- No appointment-to-visit completion sync yet.

## Stage 4 Final Acceptance Criteria

- Reception can book appointment.
- Reception can check in patient in one click.
- Reception can cancel/reschedule.
- Emergency unscheduled patient can be added as emergency appointment.
- Doctor can see Today’s Clinic.
- Doctor can open next patient quickly.
- Doctor can start Visit manually.
- Appointment does not automatically create Visit.
- Calendar view displays appointments.
- Today’s Clinic displays only today’s appointments.
- Total Booked Today counts all appointments for today regardless of status.
- Appointment rows remain visible while status changes.
- End-of-day converts remaining booked appointments to no_show.
- Previous clinic days can be reviewed.
- Appointment types are billing-ready.
- Procedure is deferred as Visit add-on.
- All tests pass.
- Migration head clean.
- No unrelated features added.

## Final Status
COMPLETE / FROZEN

---
