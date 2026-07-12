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
