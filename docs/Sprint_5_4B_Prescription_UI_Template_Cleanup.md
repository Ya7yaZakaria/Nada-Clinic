# Sprint 5.4B — Prescription UI Template Cleanup

## Goal
Clean up Visit detail by extracting the Prescription section into a partial template and restoring correct Jinja block structure.

## Scope
- Create `app/templates/visits/_prescription_section.html`.
- Rewrite `app/templates/visits/detail.html` into clean structure.
- Keep existing prescription routes unchanged.
- Keep existing forms unchanged.
- Keep existing tests unchanged unless required.

## Out of Scope
- New prescription features.
- Print engine.
- Presets.
- Diagnosis.
- Database changes.
- Migration.

## Correction
Sprint 5.4A passed tests but `visits/detail.html` contained repeated prescription markup inside page blocks. This sprint restores clean template structure and moves prescription markup to a partial.

## Acceptance Criteria
- `visits/detail.html` has only title, page_title, page_subtitle, and content blocks.
- Prescription markup lives in `_prescription_section.html`.
- Visit detail renders normally.
- Prescription add/edit/remove still works.
- Reception remains blocked by RBAC.
- No database migration.
- Full test suite passes.

## Verification
```powershell
python -m pytest tests/test_prescription_ui.py -q
python -m pytest tests/test_visit_journey_link.py tests/test_visit_model.py tests/test_prescription_ui.py -q
python -m pytest
flask db current
flask db heads
git status
git diff --stat
