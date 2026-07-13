# Sprint 6.5C — Prescription Migration to Unified Print

## Goal
Migrate prescription printing from the legacy standalone Visit print page to the unified PrintTemplate-based print engine.

## Scope
- Add unified prescription print preview route.
- Add prescription designer redirect route.
- Render prescription content using PrintTemplate.layout_json.
- Use default prescription print template automatically.
- Allow optional template_uuid query parameter for custom prescription layouts.
- Update Visit prescription Print button to unified route.
- Remove old visits.print_prescription route.
- Remove old visits/prescription_print.html template.
- Update prescription print tests.
- Add dedicated unified prescription print tests.
- Update documentation.

## Out of Scope
- Investigation print route.
- PDF generation.
- Print history.
- Print locking.
- Doctor signature.
- Logo upload.
- Multi-page printing.
- AI behavior.

## Routes Added
- GET /print/prescriptions/<visit_uuid>/designer
- GET /print/prescriptions/<visit_uuid>/preview

## Routes Removed
- GET /visits/<visit_uuid>/prescription/print

## Templates Added
- app/templates/print_templates/prescription_preview.html

## Templates Removed
- app/templates/visits/prescription_print.html

## Database Impact
No new migration.

## Permissions
Uses:
- prescriptions.view for unified prescription print preview.

Reception remains blocked because Reception does not have prescription view permission.

## Acceptance Criteria
- Doctor can open unified prescription print preview.
- Preview uses PrintTemplate layout_json.
- Preview includes patient name, MRN, date, and medication lines.
- Preview excludes diagnosis, doctor identity, safety notes, print lock, and history.
- Visit Print button points to /print/prescriptions/.
- Legacy /visits/<visit_uuid>/prescription/print route is removed.
- Old visits/prescription_print.html is removed.
- Reception cannot open unified prescription print preview.
- No new migration is added.
- Full suite passes.
