# Sprint 6.3 — Investigation Result Entry

## Goal
Allow doctors to enter investigation results for ordered items and historical/external results without prior order.

## Scope
- Hardened result service validation.
- Ordered result entry backend.
- Historical result entry backend.
- Result update/cancel service helpers.
- Patient/visit/order-item result listing helpers.
- Entered/unreviewed result listing helper.
- Result entry forms.
- Ordered result entry route/page.
- Historical result entry from Patient.
- Historical result entry from Visit.
- Result display in order detail and patient investigations.
- Tests.

## Out of Scope
- Result review UI.
- Actual file upload/storage.
- Print request.
- AI extraction.
- AI interpretation.
- Timeline integration.
- New migration.

## Acceptance Criteria
- Doctor can enter result for ordered investigation item.
- Doctor can enter historical result without order.
- Result stores lab name, date, value/text, doctor comment, abnormal flag, and attachment placeholders.
- Ordered item status updates after result entry.
- Order status updates after result entry.
- Result appears in patient investigations.
- Reception cannot enter result.
- Full tests pass.
- No migration drift.
