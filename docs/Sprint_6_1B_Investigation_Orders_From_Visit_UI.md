# Sprint 6.1B — Investigation Orders From Visit UI

## Goal
Allow doctors to create investigation orders from a Visit and add individual investigation tests.

## Scope
- Investigation forms.
- Investigation blueprint/routes.
- Investigation order creation from Visit.
- Investigation order detail page.
- Add test to order workflow.
- Cancel order item workflow.
- Patient investigations page.
- Visit detail investigations section.
- Sidebar Investigations link.
- UI tests.
- Documentation.

## Out of Scope
- Result entry UI.
- Historical result UI.
- Presets.
- Print request.
- Upload/storage.
- AI behavior.
- Timeline integration.
- New migration.

## Routes
- GET /investigations/
- GET /investigations/patients/<patient_uuid>
- GET, POST /investigations/visits/<visit_uuid>/new
- GET /investigations/orders/<order_uuid>
- POST /investigations/orders/<order_uuid>/items
- POST /investigations/items/<item_uuid>/cancel

## Acceptance Criteria
- Doctor can see investigations section inside Visit.
- Doctor can create an investigation order from Visit.
- Doctor can add an individual test to an order.
- Pending tests appear in Visit detail.
- Patient investigations page shows pending/latest sections.
- Reception cannot create investigation orders.
- No result entry, presets, print, upload, AI, or migration added.

## Verification Commands
- python -m pytest tests/test_investigation_ui.py -q
- python -m pytest tests/test_investigation_model.py tests/test_investigation_dictionary_service.py tests/test_investigation_service.py tests/test_investigation_ui.py -q
- python -m pytest
- flask db current
- flask db heads
- flask routes
- git status
- git diff --stat
