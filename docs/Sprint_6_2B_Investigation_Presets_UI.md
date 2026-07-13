# Sprint 6.2B — Investigation Presets UI

## Goal
Allow doctors to manage investigation presets and apply them to investigation orders.

## Scope
- Investigation preset forms.
- Investigation preset blueprint/routes.
- Preset list/create/edit/detail UI.
- Add/remove preset tests.
- Apply preset to investigation order.
- Sidebar Investigation Presets link.
- UI tests.
- Documentation.

## Out of Scope
- Result entry.
- Historical result UI.
- Print request.
- Upload/storage.
- AI behavior.
- Advanced missing-workup dashboard.
- New migration.

## Routes
- GET /investigation-presets/
- GET, POST /investigation-presets/new
- GET /investigation-presets/<preset_uuid>
- GET, POST /investigation-presets/<preset_uuid>/edit
- POST /investigation-presets/<preset_uuid>/deactivate
- POST /investigation-presets/<preset_uuid>/reactivate
- POST /investigation-presets/<preset_uuid>/items
- POST /investigation-presets/items/<item_uuid>/remove
- POST /investigations/orders/<order_uuid>/apply-preset

## Acceptance Criteria
- Doctor can create investigation preset.
- Doctor can add tests to preset.
- Doctor can remove tests from preset.
- Doctor can apply preset to order.
- Applied tests appear as normal editable order items.
- Reception cannot manage presets.
- Full tests pass.
- No migration drift.

## Verification Commands
- python -m pytest tests/test_investigation_presets_ui.py -q
- python -m pytest tests/test_investigation_preset_model.py tests/test_investigation_preset_service.py tests/test_investigation_presets_ui.py -q
- python -m pytest
- flask db current
- flask db heads
- flask routes
- git status
- git diff --stat
