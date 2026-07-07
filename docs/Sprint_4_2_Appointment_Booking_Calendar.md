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
