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
