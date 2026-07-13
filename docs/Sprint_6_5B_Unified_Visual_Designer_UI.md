# Sprint 6.5B — Unified Visual Designer UI

## Goal
Add a generic visual designer UI for PrintTemplate records so doctors/admins can create, select, drag, reposition, and save reusable layouts before prescription and investigation printing are migrated to the unified engine.

## Scope
- New print_templates blueprint.
- Print template list page.
- Seed default templates action.
- Create/edit template metadata.
- Deactivate/reactivate templates.
- Generic visual designer page.
- Drag-and-drop visible elements on a paper canvas.
- Save layout_json back to PrintTemplate.
- Sidebar link.
- UI tests.

## Out of Scope
- Prescription route migration.
- Investigation print route.
- Old prescription print deletion.
- Real patient/order data print preview.
- PDF generation.
- Print history.
- Print locking.
- Doctor signature.
- Logo upload.
- Multi-page printing.
- AI behavior.

## Routes
- GET  /print/templates/
- POST /print/templates/seed-defaults
- GET  /print/templates/new
- POST /print/templates/new
- GET  /print/templates/<template_uuid>/edit
- POST /print/templates/<template_uuid>/edit
- GET  /print/templates/<template_uuid>/designer
- POST /print/templates/<template_uuid>/layout
- POST /print/templates/<template_uuid>/deactivate
- POST /print/templates/<template_uuid>/reactivate

## Permissions
Uses:
- print_templates.manage

Doctor/Admin can manage print templates.
Reception remains blocked.

## Database Impact
No new migration.

## Acceptance Criteria
- Doctor/Admin can open print templates index.
- Reception cannot open print templates index.
- Doctor/Admin can seed default templates.
- Doctor/Admin can create/edit/deactivate/reactivate templates.
- Doctor/Admin can open visual designer.
- Designer shows paper canvas and layout elements.
- Layout JSON can be saved.
- Invalid layout JSON is rejected safely.
- Sidebar shows Print Templates link.
- Existing prescription print route remains unchanged until Sprint 6.5C.
- Full suite passes.
