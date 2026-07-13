# Sprint 6.2A — Investigation Presets Backend

## Goal
Create backend support for reusable investigation panels/workups.

## Scope
- Investigation preset model.
- Investigation preset item model.
- Investigation preset service.
- Apply preset to investigation order.
- Missing tests from preset using latest patient results.
- RBAC permission for investigation preset management.
- Migration.
- Model and service tests.

## Out of Scope
- Preset UI.
- Result entry UI.
- Historical result UI.
- Print request.
- Upload/storage.
- AI behavior.
- Patient Workspace UI changes.
- Timeline integration.

## Models
- InvestigationPreset
- InvestigationPresetItem

## Service
InvestigationPresetService supports:
- create/update preset
- deactivate/reactivate preset
- add/remove/list preset items
- list active/all presets
- apply preset to order
- missing tests for patient

## Rules
- Preset name is required and unique.
- Inactive tests cannot be added.
- Duplicate tests inside same preset are rejected.
- Applying a preset creates normal InvestigationOrderItem rows.
- Applying a preset skips tests already active in the order.
- Applying inactive or empty preset fails.
- Applying to cancelled order fails.
- Missing tests use latest non-cancelled results.

## Verification Commands
- flask db upgrade
- flask db current
- flask db heads
- python -m pytest tests/test_investigation_preset_model.py -q
- python -m pytest tests/test_investigation_preset_service.py -q
- python -m pytest
- git status
- git diff --stat
