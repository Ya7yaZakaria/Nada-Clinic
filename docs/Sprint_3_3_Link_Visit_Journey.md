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
