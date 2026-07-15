# Stage 11.2 — Finance Insights

## Goal

Add date-range finance insights without changing the database schema.

## Scope

- Date range filter.
- Revenue by service type.
- Expenses by category.
- Payment methods.
- Daily summary.
- Outstanding balances.
- Finance insights route and template.
- Tests.
- Documentation.

## Out of Scope

- New migration.
- Refunds.
- Installments.
- Tax/accounting ledger.
- Export.
- Heavy chart libraries.
- Payroll automation.

## Routes

- GET `/finance/insights`

## Service

`FinanceService.get_insights_summary(date_from=None, date_to=None)`

## Verification

```powershell
python -m pytest tests/test_finance_insights_stage_11_2.py -q
python -m pytest tests/test_finance_stage_11.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "finance"
git status
git diff --stat
```
