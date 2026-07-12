# Sprint 5.6 — Prescription Print Engine v1

## Goal
Add a reusable first version prescription print page.

## Scope
- Add prescription print route.
- Add standalone prescription print template.
- Add Print button inside Visit prescription card when prescription has items.
- Print patient name, MRN, date, and medication lines.
- Keep medication trade name in English.
- Keep medication patient instructions in Arabic-capable RTL layout.
- Add print-specific CSS inside the print template.
- Add UI tests for print page, print button, empty prescription redirect, and Reception blocking.

## Out of Scope
- Prescription lock-after-print.
- Prescription print history.
- Doctor identity.
- Diagnosis.
- General instructions.
- Reception print access.
- PDF generation.
- New database migration.

## Behavior
Printing opens a standalone browser print page. The page is designed for A5 browser printing and includes patient identity basics and structured medication lines only.

## Verification Commands
- python -m pytest tests/test_prescription_ui.py -q
- python -m pytest tests/test_prescription_model.py tests/test_prescription_service.py tests/test_prescription_ui.py -q
- python -m pytest
- flask db current
- flask db heads
