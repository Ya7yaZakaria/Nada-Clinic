# Stage 6 — Investigation Module Freeze Review

## Goal
Freeze-review Stage 6 Investigations after completing investigation dictionaries, orders, presets, result entry, historical results, result review, patient workspace investigation display, timeline events, and unified investigation request printing.

## Scope Reviewed
- Investigation dictionaries.
- Investigation tests.
- Investigation orders from Visit.
- Investigation order detail.
- Add/cancel investigation order items.
- Investigation presets backend and UI.
- Apply preset to investigation order.
- Ordered result entry.
- Enter pending ordered results from the current Visit while preserving the original ordered Visit.
- Historical/external result entry from Patient and Visit contexts.
- Result review workflow.
- Pending result review queue.
- Patient Workspace investigation section.
- Timeline events for investigation ordered, result entered, and result reviewed.
- Unified investigation request print preview.
- RBAC and Reception blocking.
- Stage 5 prescription regression after unified print migration.

## Stage 5 Regression Reviewed
- Drug dictionaries.
- Drug database.
- Prescription model/service/UI.
- Prescription presets.
- Apply prescription preset inside Visit.
- Unified prescription print preview.
- Legacy prescription print route/template removal.
- Reception blocking.

## Confirmed Architecture
- Patient remains root entity.
- Visit remains the clinical encounter.
- InvestigationOrder belongs to Patient and may link to ordered_visit and Journey.
- InvestigationResult supports ordered and historical/external workflows.
- Result entry and result review are separate workflows.
- Investigation request printing uses the unified PrintTemplate engine.
- Result report printing remains out of scope until Documents/Storage.

## Cleanup Performed
- Ordered result current Visit context fix: results can now be entered from a later Visit and stored with `result_visit_id` pointing to the current Visit while `ordered_visit_id` remains the original ordering Visit.
- Cleaned the Visit investigation test choice label separator from mojibake/question mark to a normal dash.

## Out of Scope Confirmed
- No real file upload/storage.
- No document repository.
- No PDF generation.
- No result report printing.
- No lab integration.
- No AI interpretation.
- No automatic diagnosis.
- No alerts/notifications.
- No billing/finance.
- No new database migration in this freeze sprint.

## Verification Commands
- Stage 5 prescription regression tests.
- Stage 6 investigation model/service/UI/result/review/print tests.
- Shared patient workspace, visit, timeline, RBAC tests.
- Full test suite.
- flask db current.
- flask db heads.
- flask routes.
- Static route/template checks.

## Acceptance Criteria
- Full suite passes.
- Migration current/head remains 20260713_0063.
- Prescription unified print remains working.
- Investigation unified print remains working.
- Investigation orders, presets, results, reviews, patient workspace, and timeline tests pass.
- Reception remains blocked by RBAC.
- Legacy prescription print template remains removed.
- Only cleanup/doc changes remain pending after verification.

## Freeze Decision
Stage 6 Investigation Module can be frozen after successful verification output is reviewed and committed.

## Recommended Next Stage
Stage 7 — Documents & Storage.

Rationale:
- Investigation results already contain attachment placeholders.
- Stage 7 should implement real file/document storage before result report printing, ultrasound images, surgery documents, and future AI document summarization.
