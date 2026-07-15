# Stage 10 — Partner Freeze Review

## Freeze Criteria

- Partner can be created and edited from Patient Workspace.
- Partner card appears in Patient Workspace.
- SA history supports notes and optional upload only.
- Latest SA appears in Partner card.
- Partner prescription uses existing Prescription + PrescriptionItem.
- Existing Visit prescription flow still works.
- No structured SA parameters added.
- No PartnerPrescription tables added.
- Reception remains blocked.
- Full regression passes.
- Migration current/head is clean.
- Working tree clean after commit/push.

## Verification Commands

```powershell
flask db upgrade
python -m pytest tests/test_partner_stage_10.py -q
python -m pytest tests/test_prescription_model.py -q
python -m pytest tests/test_prescription_service.py -q
python -m pytest tests/test_prescription_ui.py -q
python -m pytest tests/test_prescription_unified_print.py -q
python -m pytest tests/test_document_service.py -q
python -m pytest tests/test_document_ui.py -q
python -m pytest tests/test_patient_workspace.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "partners"
git status
git diff --stat
```
