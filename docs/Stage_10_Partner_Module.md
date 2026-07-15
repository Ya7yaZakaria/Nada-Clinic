# Stage 10 — Partner Module

## Status

Implemented as one stage-wide script.

## Goal

Add simple practical Partner/Husband support linked to Patient Workspace.

## Scope

- Partner model.
- One active partner per patient.
- PartnerSemenAnalysis model.
- SA history as date + notes + optional upload only.
- No structured SA parameters.
- SA upload uses PatientDocument with document_type `semen_analysis`.
- Existing Prescription model extended with `prescription_target` and `partner_id`.
- Partner prescriptions use existing PrescriptionItem medication rows.
- No PartnerPrescription tables.
- Patient Workspace Partner card.
- Partner add/edit.
- SA add/history/detail.
- Partner prescription create/detail/items/edit/remove.
- RBAC.
- Tests.
- Documentation.

## Deferred

- Structured semen analysis fields.
- AI SA interpretation.
- OCR.
- Partner as full Patient.
- Partner dashboard.
- Partner prescription printing.
- Full male infertility module.
- Multiple active partners.
