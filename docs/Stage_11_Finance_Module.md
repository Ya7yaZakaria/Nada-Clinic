# Stage 11 — Embedded Finance + Insights

## Status

Sprint 11.1 implementation script.

## Goal

Capture finance inside the natural clinic workflow:
- Appointment booking
- Visit/procedure creation
- Surgery scheduling/completion
- Clinic expenses

## Implemented in Sprint 11.1

- FinanceCharge model.
- FinancePayment model.
- FinanceExpense model.
- FinanceService.
- Embedded payment fields in Appointment.
- Embedded payment fields in Visit.
- Surgery payment method and Finance sync.
- Finance dashboard.
- Clinic expenses page.
- Patient Workspace finance summary.
- Finance RBAC.
- Tests.

## Design Decision

No separate Add Charge button inside Appointment, Visit, or Surgery.
Finance records are created automatically from the service layer.

## Deferred to Sprint 11.2

- Advanced date-range insights.
- Charts.
- Revenue by service type.
- Expenses by category charts.
- Net profit trend.
- Export.
- Refunds.
- Accounting ledger.
