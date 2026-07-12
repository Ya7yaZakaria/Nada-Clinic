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
