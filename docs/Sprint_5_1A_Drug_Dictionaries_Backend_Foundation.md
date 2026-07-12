# Sprint 5.1A — Drug Dictionaries Backend Foundation

## Goal
Create AI-ready backend foundation for editable medication dictionaries.

## Scope
This sprint adds backend-only medication dictionary foundations.

## Included
- DrugCategory model.
- DrugForm model.
- DrugRoute model.
- DrugSafetyStatus model.
- DrugDictionaryService.
- Default dictionary seed method.
- RBAC permission: drug_settings.manage.
- Admin and Doctor can manage drug settings.
- Reception is blocked.
- Alembic migration for dictionary tables.
- Model and service tests.

## Out of Scope
- Drug database model.
- Prescription model.
- Prescription UI.
- Print engine.
- Routes.
- Templates.
- AI suggestions.
- Drug safety automation.
- Reception medication access.

## Database Tables
- drug_categories
- drug_forms
- drug_routes
- drug_safety_statuses

## Permission
- drug_settings.manage

## Role Access
- Admin: allowed.
- Doctor: allowed.
- Reception: blocked.

## Design Decisions
- Medication dictionary values are structured.
- Dictionary values are editable by authorized users.
- Dictionary values are not random free text.
- Dictionary values are not permanently hardcoded in code.
- This supports future AI-ready structured medication data.
- Safety statuses are doctor-only internal references.
- No clinical decision support is implemented yet.

## Verification
- tests/test_drug_dictionaries_model.py: 3 passed.
- tests/test_drug_dictionaries_crud.py: 9 passed.
- Full test suite: 187 passed, 225 warnings.
- Migration current/head: 20260712_0051.
- No UI or prescription features added.

## Status
Complete.
