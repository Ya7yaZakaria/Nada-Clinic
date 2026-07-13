# Sprint 6.5A — Unified Print Template Backend

## Goal
Create a reusable backend foundation for visual print templates that can later serve both prescription printing and investigation request printing.

## Scope
- Generic PrintTemplate model.
- Generic PrintTemplateService.
- Document types:
  - prescription
  - investigation_request
- JSON-based layout storage.
- Paper size storage in millimeters.
- Default template support.
- Active/inactive template support.
- One default template per document type enforced by service.
- RBAC permission for print template management.
- Migration.
- Model/service/RBAC tests.

## Out of Scope
- Visual drag-and-drop designer UI.
- Prescription route migration.
- Investigation print route.
- Old prescription print deletion.
- Print preview page.
- PDF generation.
- Print history.
- Print locking.
- Doctor signature.
- Logo upload.
- Multi-page printing.
- AI behavior.

## Database Impact
Creates table:

- print_templates

Fields:
- id
- uuid
- name
- document_type
- paper_width_mm
- paper_height_mm
- layout_json
- is_default
- is_active
- created_by_user_id
- updated_by_user_id
- created_at
- updated_at

## Permissions
Adds:
- print_templates.manage

Doctor/Admin can manage print templates.
Reception remains blocked.

## Acceptance Criteria
- PrintTemplate table exists.
- Prescription and investigation_request document types are supported.
- Default templates can be created idempotently.
- Layout JSON can be stored and updated.
- Same template name is allowed across different document types.
- Duplicate names are blocked within the same document type.
- Only one default active template is kept per document type by service.
- Doctor/Admin receive print_templates.manage.
- Reception does not receive print_templates.manage.
- Existing prescription print remains temporarily until Sprint 6.5C migration.
- Migration applies cleanly.
- Full suite passes.
