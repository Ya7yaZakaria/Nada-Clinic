# Architecture

This file is a current structural map generated from the repository tree during the 2026-08-09 documentation cleanup. It describes files that exist; behavioral details still belong to source and tests.

## Application layers

- `app/models/` — SQLAlchemy domain models.
- `app/services/` — domain/service logic.
- `app/routes/` — Flask route modules.
- `app/forms/` — Flask-WTF form definitions.
- `app/templates/` — Jinja templates by workflow/domain.
- `app/static/` — CSS and JavaScript assets.
- `migrations/` — Alembic/Flask-Migrate history.
- `tests/` — pytest suite organized by domain.

## Model modules

- `appointment`
- `clinic_day_state`
- `document`
- `drug`
- `drug_dictionary`
- `finance`
- `investigation`
- `investigation_preset`
- `journey`
- `partner`
- `patient`
- `permission`
- `prescription`
- `prescription_preset`
- `print_template`
- `role`
- `setting`
- `surgery`
- `ultrasound`
- `user`
- `visit`

## Service modules

- `appointment_service`
- `auth_service`
- `clinic_day_service`
- `clinic_day_state_service`
- `clinic_ultrasound_service`
- `dashboard_service`
- `demo_data_service`
- `development_role_preview_service`
- `document_service`
- `drug_dictionary_service`
- `drug_service`
- `external_ultrasound_service`
- `finance_service`
- `investigation_dictionary_service`
- `investigation_preset_service`
- `investigation_service`
- `journey_service`
- `partner_semen_analysis_service`
- `partner_service`
- `patient_dashboard_service`
- `patient_service`
- `prescription_preset_service`
- `prescription_service`
- `print_template_service`
- `rbac_service`
- `settings_service`
- `surgery_analytics_service`
- `surgery_service`
- `timeline_service`
- `visit_service`

## Route modules

- `admin`
- `appointments`
- `auth`
- `development`
- `documents`
- `drug_settings`
- `drugs`
- `finance`
- `investigation_presets`
- `investigations`
- `journeys`
- `main`
- `partners`
- `patients`
- `prescription_presets`
- `print_templates`
- `settings`
- `surgeries`
- `today_clinic`
- `ultrasounds`
- `visits`

## Form modules

- `appointment_forms`
- `auth_forms`
- `document_forms`
- `drug_dictionary_forms`
- `drug_forms`
- `finance_forms`
- `investigation_forms`
- `investigation_preset_forms`
- `investigation_result_forms`
- `investigation_review_forms`
- `journey_forms`
- `partner_forms`
- `patient_forms`
- `prescription_forms`
- `prescription_preset_forms`
- `print_template_forms`
- `settings_forms`
- `surgery_forms`
- `ultrasound_forms`
- `visit_forms`

## Template domains

- `admin/`
- `appointments/`
- `auth/`
- `clinic/`
- `documents/`
- `drug_settings/`
- `drugs/`
- `errors/`
- `finance/`
- `investigation_presets/`
- `investigations/`
- `journeys/`
- `partners/`
- `patients/`
- `placeholders/`
- `prescription_presets/`
- `print_templates/`
- `settings/`
- `surgeries/`
- `ultrasounds/`
- `visits/`

## Source-of-truth rule

For implementation details, permissions, route behavior, migrations, and validation, inspect the current source and tests. Historical stage documents under `docs/history/` are evidence of prior checkpoints, not authority over current code.
