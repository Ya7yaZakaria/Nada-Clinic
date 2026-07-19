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