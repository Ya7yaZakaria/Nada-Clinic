# Stage 2 — Sprint 2.4 Patient Workspace v1

## Goal

Refine the Patient Workspace as the fast patient-centered entry point.

## Scope

- Improved patient workspace header
- MRN/name/age/phone/address display
- Name display based on system language
- Virgin badge/check display
- Patient identity card
- Clinical Snapshot placeholder
- Recent Visits placeholder
- Quick Actions placeholder
- Workspace tests
- Documentation

## Out of Scope

- Real Visit implementation
- Clinical notes
- Timeline implementation
- Appointment integration
- Investigations
- Documents
- Partner module

## Workspace Route

- GET /patients/<uuid>

## Header

- MRN
- Display name based on localization.language
- Age
- Phone
- Address

## Quick Actions

- New Visit placeholder
- Visits placeholder
- Edit active link

## Acceptance Criteria

- Patient Workspace opens quickly.
- Header shows MRN/name/age/phone/address.
- Name follows system language setting.
- Virgin check is visible.
- Clinical Snapshot placeholder exists.
- Recent Visits placeholder exists.
- Quick actions show New Visit / Visits / Edit.
- New Visit and Visits are disabled placeholders.
- No real Visit implementation added.
- Tests pass.
- Migration head remains clean.
