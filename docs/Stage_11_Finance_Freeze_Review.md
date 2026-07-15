# Stage 11 — Finance Freeze Review

## Sprint 11.1 Verification

Run:

```powershell
flask db upgrade
python -m pytest tests/test_finance_stage_11.py -q
python -m pytest tests/test_appointment_crud.py -q
python -m pytest tests/test_appointment_workflow.py -q
python -m pytest tests/test_patient_workspace.py -q
python -m pytest tests/test_surgery_stage_9.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "finance"
git status
git diff --stat
```

## Freeze checklist

- Models reviewed.
- Migration reviewed.
- Embedded Appointment finance reviewed.
- Embedded Visit finance reviewed.
- Embedded Surgery finance reviewed.
- Expense workflow reviewed.
- Patient Workspace finance reviewed.
- RBAC reviewed.
- Tests reviewed.
- Documentation reviewed.
- No standalone Add Charge button added to modules.
