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
