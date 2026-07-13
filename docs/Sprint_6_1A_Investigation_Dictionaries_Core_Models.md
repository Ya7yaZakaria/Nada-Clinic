# Sprint 6.1A — Investigation Dictionaries + Core Models

## Goal
Create the backend foundation for the Investigations Module.

## Scope
- Investigation categories.
- Investigation tests.
- Investigation orders.
- Investigation order items.
- Investigation results.
- Result without prior order.
- Separate ordered visit and result visit.
- Lab name and result date.
- Result value/unit/reference range/text.
- Doctor comment.
- Abnormal flag.
- Attachment placeholder for Stage 7.
- Latest result service.
- Pending ordered result service.
- Missing tests from required list foundation.
- Investigation RBAC permissions.
- Migration.
- Tests.

## Out of Scope
- UI.
- Presets.
- Printing.
- Real file upload/storage.
- AI extraction.
- Lab integration.
- Patient Workspace integration.
- Timeline integration.

## Design Decisions
- Historical/external results can be recorded without prior order.
- Ordered visit and result visit are separate.
- CBC and complex investigations start as one test with text/report fields.
- Upload/storage is prepared only with placeholders.
- AI-ready data exists, but no AI behavior is added.

## Verification Commands
- flask db upgrade
- flask db current
- flask db heads
- python -m pytest tests/test_investigation_model.py -q
- python -m pytest tests/test_investigation_dictionary_service.py -q
- python -m pytest tests/test_investigation_service.py -q
- python -m pytest
- git status
- git diff --stat
