# Sprint 6.5D — Investigation Print Using Unified Designer

## Goal
Add investigation request printing using the unified PrintTemplate-based print engine.

## Scope
- Add unified investigation request preview route.
- Add investigation request designer redirect route.
- Render investigation order content using PrintTemplate.layout_json.
- Use default investigation request print template automatically.
- Allow optional template_uuid query parameter for custom investigation request layouts.
- Add Print request button to investigation order detail.
- Add dedicated unified investigation print tests.
- Update documentation.

## Out of Scope
- PDF generation.
- Print history.
- Print locking.
- Doctor signature.
- Logo upload.
- Result report printing.
- Lab integration.
- AI behavior.
- New database migration.

## Routes Added
- GET /print/investigations/<order_uuid>/designer
- GET /print/investigations/<order_uuid>/preview

## Templates Added
- app/templates/print_templates/investigation_request_preview.html

## Database Impact
No new migration.

## Permissions
Uses:
- investigations.view for unified investigation request print preview.

Reception remains blocked because Reception does not have investigations view permission.

## Acceptance Criteria
- Doctor can open unified investigation request print preview.
- Preview uses PrintTemplate.layout_json.
- Preview includes patient name, MRN, date, instruction, and investigation lines.
- Preview excludes result report printing.
- Investigation order detail shows Print request button when the order has items.
- Empty order redirects with warning.
- Reception cannot open unified investigation request print preview.
- No new migration is added.
- Full suite passes.
