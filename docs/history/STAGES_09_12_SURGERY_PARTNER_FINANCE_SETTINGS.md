# Stages 09 12 Surgery Partner Finance Settings

Historical sprint/stage source material consolidated verbatim. It is retained for traceability and does not override current code.

## Included legacy sources

- `Sprint_12_1_Settings_UI_Foundation.md`
- `Sprint_12_2_Appearance_Night_Mode_RTL.md`
- `Sprint_12_3_Clinic_Profile_Settings.md`
- `Sprint_12_4_Workflow_Defaults.md`
- `Stage_10_Partner_Freeze_Review.md`
- `Stage_10_Partner_Module.md`
- `Stage_11_2_Finance_Insights.md`
- `Stage_11_Finance_Freeze_Review.md`
- `Stage_11_Finance_Module.md`
- `Stage_12_Settings_And_Personalization.md`
- `Stage_12_Settings_And_Personalization_Freeze_Review.md`
- `Stage_9_Surgery_Freeze_Review.md`
- `Stage_9_Surgery_Module.md`

---

## Legacy source: `Sprint_12_1_Settings_UI_Foundation.md`

# Sprint 12.1 — Settings UI Foundation

## Goal

Create a Settings dashboard and grouped settings editor using the existing `Setting` model and `SettingsService`.

## Scope

- Add `/settings/`.
- Add settings group pages.
- Add single setting edit page.
- Add seed defaults action.
- Add choice validation for key personalization settings.
- Add Stage 12 personalization keys.
- Add sidebar link.
- Add tests.
- Add documentation.

## Out of Scope

- Full dark mode CSS.
- Full Arabic translation.
- Per-user preferences.
- Logo upload.
- Notification settings.
- Permission editor.

## Database Impact

No schema migration expected.

New default setting keys are seeded through `SettingsService.DEFAULT_SETTINGS`.

## Routes

- `GET /settings/`
- `GET /settings/<group>`
- `GET, POST /settings/edit/<setting_key>`
- `POST /settings/seed-defaults`

## Permissions

- `settings.view`
- `settings.manage`

Existing RBAC is preserved.

## Verification

```powershell
python -m pytest tests/test_settings.py -q
python -m pytest tests/test_settings_ui_stage_12.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "settings"
git status
git diff --stat
```

---

## Legacy source: `Sprint_12_2_Appearance_Night_Mode_RTL.md`

# Sprint 12.2 — Appearance, Night Mode, RTL Foundation

## Goal

Make Stage 12 appearance and localization settings affect the actual UI shell.

## Scope

- Apply theme settings to the base layout.
- Support light, dark, and auto theme modes.
- Apply language settings to `html lang`.
- Apply Arabic direction with `dir="rtl"`.
- Add data attributes for accent color, font size, and density preferences.
- Add CSS variables and layout rules for dark mode, accents, density, and RTL foundation.
- Add tests.

## Out of Scope

- Full Arabic translation.
- Per-user preferences.
- Logo upload.
- Print-specific redesign.
- Advanced theme builder.

## Database Impact

No migration required.

Sprint 12.2 reuses existing Stage 12.1 settings keys.

## Verification

```powershell
python -m pytest tests/test_appearance_personalization_stage_12.py -q
python -m pytest tests/test_settings_ui_stage_12.py -q
python -m pytest tests/test_settings.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
git status
git diff --stat
```

---

## Legacy source: `Sprint_12_3_Clinic_Profile_Settings.md`

# Sprint 12.3 — Clinic Profile Settings

## Goal

Add a dedicated clinic profile settings page using the existing Setting model.

## Scope

- Add clinic profile helper methods to SettingsService.
- Inject clinic profile into the global template context.
- Apply clinic name and short name to the base shell brand/title.
- Add `/settings/clinic-profile`.
- Add Clinic Profile shortcut card on the Settings dashboard.
- Add tests for access, display, updates, and shell brand integration.

## Out of Scope

- Logo upload.
- File storage for logo.
- Doctor profile records.
- Print template redesign.
- Full Arabic translation.
- Per-user preferences.

## Database Impact

No schema migration required.

Sprint 12.3 reuses existing clinic settings keys:
- clinic.name
- clinic.short_name
- clinic.phone
- clinic.whatsapp
- clinic.address
- clinic.logo_path
- clinic.default_doctor_name

## Verification

```powershell
python -m pytest tests/test_clinic_profile_settings_stage_12.py -q
python -m pytest tests/test_appearance_personalization_stage_12.py -q
python -m pytest tests/test_settings_ui_stage_12.py -q
python -m pytest tests/test_settings.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "settings"
git status
git diff --stat
```

---

## Legacy source: `Sprint_12_4_Workflow_Defaults.md`

# Sprint 12.4 — Workflow Defaults

## Goal

Make the existing workflow default landing setting operational.

## Scope

- Resolve `workflow.default_landing_page` to safe route endpoints.
- Redirect successful login to the configured default landing page.
- Keep a safe dashboard fallback for invalid targets.
- Show workflow default status in Settings dashboard.
- Add focused tests.

## Out of Scope

- Dashboard redesign.
- Admin Home redesign.
- Per-user landing preferences.
- New workflow database tables.
- Notifications.
- Follow-up engine implementation.

## Database Impact

No schema migration required.

Sprint 12.4 reuses existing settings:
- workflow.default_landing_page
- workflow.enable_today_clinic
- workflow.enable_patient_workspace
- workflow.enable_followup_tracker

## Verification

```powershell
python -m pytest tests/test_workflow_defaults_stage_12.py -q
python -m pytest tests/test_auth.py -q
python -m pytest tests/test_settings_ui_stage_12.py -q
python -m pytest tests/test_settings.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "settings|auth"
git status
git diff --stat
```

---

## Legacy source: `Stage_10_Partner_Freeze_Review.md`

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

---

## Legacy source: `Stage_10_Partner_Module.md`

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

---

## Legacy source: `Stage_11_2_Finance_Insights.md`

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

---

## Legacy source: `Stage_11_Finance_Freeze_Review.md`

# Stage 11 — Finance Freeze Review

## Status

Stage 11 Finance is frozen.

## Completed Scope

### Sprint 11.1 — Embedded Finance Capture

- Added FinanceCharge.
- Added FinancePayment.
- Added FinanceExpense.
- Added FinanceService.
- Added embedded Appointment fee/payment capture.
- Added embedded Visit/procedure fee/payment capture.
- Synced Surgery fee/paid/payment method to Finance.
- Added clinic expenses.
- Added Patient Workspace finance summary.
- Added Finance dashboard.
- Added finance RBAC.

### Sprint 11.2 — Finance Insights Dashboard

- Added `/finance/insights`.
- Added date-range filter.
- Added revenue by service type.
- Added expenses by category.
- Added payment method breakdown.
- Added daily summary.
- Added outstanding balances.
- Added finance insights tests.
- Added documentation.

## Out of Scope / Deferred

- Refunds.
- Export.
- Full accounting ledger.
- Payroll automation.
- Tax accounting.
- Installments.
- Heavy chart library.
- AI finance predictions.

## Database Review

- Sprint 11.1 migration: `20260715_0069_add_embedded_finance`.
- Sprint 11.2 required no migration.
- Current/head after verification: `20260715_0069`.

## Permissions Review

- `finance.view`
- `finance.collect`
- `finance.manage`
- `finance.insights`

Reception can view Finance dashboard according to current RBAC but cannot manage expenses.
Doctor/Admin can use finance workflows according to assigned permissions.

## Route Review

- `GET /finance/`
- `GET /finance/insights`
- `GET /finance/expenses`
- `GET, POST /finance/expenses/new`
- `GET, POST /finance/expenses/<expense_uuid>/edit`

## Tests Review

Verified before freeze:

- `tests/test_finance_stage_11.py`
- `tests/test_finance_insights_stage_11_2.py`
- `tests/test_rbac.py`
- Full regression

Final verification:

- Full regression: `425 passed`
- Migration current/head: `20260715_0069`
- Working tree clean after push.

## Git Review

Stage 11 commits:

- `9dc854e feat(finance): add embedded finance capture`
- `d63a7e2 feat(finance): add finance insights dashboard`

## Freeze Checklist

- Models reviewed: passed.
- Migrations reviewed: passed.
- Routes reviewed: passed.
- Services reviewed: passed.
- Forms reviewed: passed.
- Templates reviewed: passed.
- Permissions reviewed: passed.
- Tests reviewed: passed.
- Documentation reviewed: passed.
- No migration drift: passed.
- No unrelated changes: passed.

## Final Decision

Stage 11 Finance is closed and frozen.

Next stage: Stage 12 — Notifications.

---

## Legacy source: `Stage_11_Finance_Module.md`

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

---

## Legacy source: `Stage_12_Settings_And_Personalization.md`

# Stage 12 — Settings & Personalization

## Goal

Build a practical Settings & Personalization layer for Nada Clinic System.

## Architecture

Stage 12 reuses the existing global `Setting` model and `SettingsService`.

No new settings table is introduced in Sprint 12.1.

## Included

- Settings dashboard.
- Grouped settings editor.
- Single setting edit workflow.
- Seed defaults action.
- Appearance personalization keys.
- Localization language choices.
- RBAC protection.
- Tests and documentation.

## Deferred

- Full dark mode CSS implementation.
- Full Arabic translation.
- Per-user preferences.
- Notifications.
- Advanced permission editor.
- Logo upload pipeline.

## Stage 12 Sprints

- Sprint 12.1 Settings UI Foundation.
- Sprint 12.2 Appearance, Night Mode, and RTL Foundation.
- Sprint 12.3 Clinic Profile Settings.
- Sprint 12.4 Workflow Defaults and Admin Home.
- Sprint 12.5 Freeze Review.

---

## Legacy source: `Stage_12_Settings_And_Personalization_Freeze_Review.md`

# Stage 12 — Settings & Personalization Freeze Review

## Status

Frozen after Sprint 12.4 Workflow Defaults.

## Completed Scope

- Settings dashboard.
- Grouped settings editor.
- Single setting edit workflow.
- Seed default settings action.
- Appearance personalization foundation.
- Dark / night mode foundation.
- Accent color support.
- Font size support.
- Sidebar, card, and table density support.
- Localization language setting.
- Arabic RTL / English LTR foundation.
- Clinic Profile settings page.
- Global clinic profile template context.
- Workflow default landing setting.
- Login redirect support for configured workflow landing page.
- Settings RBAC protection.
- Stage 12 tests and documentation.

## Verified Components

### Models

- Existing Setting model reused.
- No new settings table added.
- No per-user preference model added.

### Services

- SettingsService manages defaults, grouped settings, choice validation, UI preferences, clinic profile, and workflow defaults.
- Existing RBACService protects Settings access.

### Routes

Verified settings routes:

- GET /settings/
- POST /settings/seed-defaults
- GET /settings/clinic-profile
- GET /settings/<group>
- GET/POST /settings/edit/<setting_key>

Verified auth impact:

- Successful login respects workflow.default_landing_page.
- Invalid landing keys fall back to Dashboard.

### Templates

- base.html uses global UI preferences.
- Settings dashboard renders grouped settings.
- Settings group page renders setting list.
- Settings edit page renders choice/boolean/integer/string values.
- Clinic profile page renders clinic identity fields.
- Settings dashboard renders workflow defaults.

### Permissions

- settings.view protects Settings read access.
- settings.manage protects edit and seed defaults.
- Reception remains blocked from Settings workflows where expected.

### Audit

- No new audit table required in Stage 12.
- Existing Setting.updated_at behavior remains sufficient for this sprint stage.

### Database / Migration

- No new migration added in Stage 12 freeze.
- Migration current/head verified separately by command output.

## Verified Test Coverage

Stage 12 focused tests:

- tests/test_settings.py
- tests/test_settings_ui_stage_12.py
- tests/test_appearance_personalization_stage_12.py
- tests/test_clinic_profile_settings_stage_12.py
- tests/test_workflow_defaults_stage_12.py
- tests/test_rbac.py

Full regression must pass before commit.

## Confirmed Out of Scope

- Full Arabic app-wide translation.
- Per-user preferences.
- Logo upload pipeline.
- Multi-branch clinic settings.
- Advanced permission builder.
- Notifications.
- WhatsApp/SMS integration.
- Email system.
- Backup/deployment.
- AI personalization.
- Complex theme designer.

## Acceptance Criteria

- Settings UI works.
- Grouped settings work.
- Settings edit workflow works.
- Dark mode foundation works.
- Arabic direction foundation works.
- Clinic profile settings work.
- Workflow default login landing works.
- RBAC protection works.
- No migration drift.
- Full regression passes.
- Documentation updated.
- Working tree clean after commit/push.

## Verification Commands

```powershell
python -m pytest tests/test_settings.py -q
python -m pytest tests/test_settings_ui_stage_12.py -q
python -m pytest tests/test_appearance_personalization_stage_12.py -q
python -m pytest tests/test_clinic_profile_settings_stage_12.py -q
python -m pytest tests/test_workflow_defaults_stage_12.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest
flask db current
flask db heads
flask routes | Select-String "settings|auth"
git status
git diff --stat
```

## Freeze Decision

Stage 12 Settings & Personalization is ready to freeze once the verification commands pass and the freeze documentation commit is pushed.

---

## Legacy source: `Stage_9_Surgery_Freeze_Review.md`

# Stage 9 — Surgery Freeze Review

## Status

Frozen after cleanup.

## Scope Verified

- SurgeryCase model.
- Migration 20260715_0067.
- SurgeryService workflow.
- SurgeryAnalyticsService.
- Surgery dashboard.
- Surgery list.
- Surgery calendar.
- Surgery detail.
- Create surgery from dashboard.
- Create surgery from patient context.
- Create surgery from visit context.
- Complete surgery.
- Cancel surgery.
- Postpone surgery.
- Mark postponed surgery back as scheduled.
- Patient Timeline integration.
- Patient Surgical History / Surgery Records section.
- RBAC permissions.
- Module-level insights foundation.
- Documentation.
- Tests.

## Design Decisions Confirmed

- Surgery is an independent operational module.
- Surgery starts only when scheduled.
- No planned status exists.
- Visit plan can mention surgery without creating SurgeryCase.
- Surgery appears inside Patient Timeline like Visit but with Surgery badge/color.
- Surgery appears in Patient Workspace as surgical history/records, not as a separate Patient Workspace tab.
- Surgery insights are module-level analytics, not per-surgery insights.
- Finance is light only; full Finance remains deferred.

## Cleanup Completed

- Added dashboard Postponed / Cancelled section.
- Added mark-postponed-as-scheduled route and UI action.
- Added tests for dashboard attention section and mark scheduled workflow.
- Added freeze documentation.

## Deferred

- Surgery documents and consent.
- PatientDocument.surgery_case_id.
- Operation report printing.
- Full Finance module.
- AI/OCR.
- Anesthesia module.
- OR inventory.
- Hospital admission workflow.
- Advanced chart analytics.

## Verification Commands

```powershell
flask db current
flask db heads
python -m pytest tests/test_surgery_stage_9.py -q
python -m pytest tests/test_rbac.py -q
python -m pytest tests/test_patient_workspace.py -q
python -m pytest
flask routes | Select-String "surgeries"
git status
git diff --stat
```

## Freeze Acceptance Criteria

- Full regression passes.
- Migration current/head is 20260715_0067.
- Surgery dashboard shows scheduled, upcoming, completed, postponed/cancelled.
- Postponed surgery can be marked scheduled.
- Invalid mark scheduled action is rejected.
- Patient timeline still shows surgery events.
- RBAC still blocks Reception.
- No migration drift.
- No backup/script files committed.
- Working tree clean after commit/push.

---

## Legacy source: `Stage_9_Surgery_Module.md`

# Stage 9 — Surgery Module

## Status

Implemented as one stage-wide script.

## Goal

Create an operational Surgery module for scheduled operations.

## Scope

- SurgeryCase model.
- SurgeryService.
- SurgeryAnalyticsService.
- Surgery forms.
- Surgery routes.
- Surgery dashboard.
- Surgery list.
- Surgery calendar grouped by date.
- Surgery detail.
- Create surgery from dashboard.
- Create surgery from patient context.
- Create surgery from visit context.
- Complete surgery.
- Cancel surgery.
- Postpone surgery.
- Patient Surgical History / Surgery Records section.
- Patient Timeline surgery events.
- Basic module-level insights.
- RBAC.
- Tests.

## Design Decisions

- Surgery starts when scheduled.
- No planned status.
- Visit plan can mention surgery without creating SurgeryCase.
- Surgery appears in Patient Timeline like Visit, with Surgery badge.
- Surgery insights are module-level analytics, not per-surgery insights.
- Finance is light only: fee, paid, payment status.
- Documents/consent are deferred.

## Deferred

- Consent upload.
- Operation report documents.
- PatientDocument.surgery_case_id.
- AI summaries.
- OCR.
- Full finance module.
- Anesthesia module.
- OR inventory.
- Admission workflow.
- Advanced charts.

## Verification

Run:

- flask db upgrade
- python -m pytest tests/test_surgery_stage_9.py -q
- python -m pytest tests/test_rbac.py -q
- python -m pytest tests/test_patient_workspace.py -q
- python -m pytest
- flask db current
- flask db heads
- flask routes

## Freeze Cleanup

Added before freeze:
- Dashboard Postponed / Cancelled section.
- Mark Scheduled action for postponed surgeries.
- Tests for postponed-to-scheduled workflow.
- Stage 9 freeze review document.

---
