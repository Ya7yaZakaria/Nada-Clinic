"""reconcile model indexes

Revision ID: 20260808_0072
Revises: 20260720_0071
Create Date: 2026-08-08
"""

from alembic import op


revision = "20260808_0072"
down_revision = "20260720_0071"
branch_labels = None
depends_on = None


_DRUG_UNIQUE_INDEXES = (
    ("drug_categories", "ix_drug_categories_code", "code"),
    ("drug_categories", "ix_drug_categories_uuid", "uuid"),
    ("drug_forms", "ix_drug_forms_code", "code"),
    ("drug_forms", "ix_drug_forms_uuid", "uuid"),
    ("drug_routes", "ix_drug_routes_code", "code"),
    ("drug_routes", "ix_drug_routes_uuid", "uuid"),
    ("drug_safety_statuses", "ix_drug_safety_statuses_code", "code"),
    ("drug_safety_statuses", "ix_drug_safety_statuses_uuid", "uuid"),
    ("drugs", "ix_drugs_uuid", "uuid"),
)

_SURGERY_INDEXES = (
    ("ix_surgery_cases_cancelled_by_user_id", "cancelled_by_user_id"),
    ("ix_surgery_cases_completed_at", "completed_at"),
    ("ix_surgery_cases_completed_by_user_id", "completed_by_user_id"),
    ("ix_surgery_cases_created_by_user_id", "created_by_user_id"),
    ("ix_surgery_cases_doctor_id", "doctor_id"),
    ("ix_surgery_cases_payment_status", "payment_status"),
    ("ix_surgery_cases_postponed_by_user_id", "postponed_by_user_id"),
    ("ix_surgery_cases_priority", "priority"),
)


def _make_drug_indexes_unique():
    for table_name, index_name, column_name in _DRUG_UNIQUE_INDEXES:
        op.drop_index(index_name, table_name=table_name)
        op.create_index(index_name, table_name, [column_name], unique=True)


def _restore_legacy_drug_indexes():
    for table_name, index_name, column_name in _DRUG_UNIQUE_INDEXES:
        op.drop_index(index_name, table_name=table_name)
        op.create_index(index_name, table_name, [column_name], unique=False)


def upgrade():
    _make_drug_indexes_unique()

    for index_name, column_name in _SURGERY_INDEXES:
        op.create_index(index_name, "surgery_cases", [column_name], unique=False)


def downgrade():
    for index_name, _column_name in reversed(_SURGERY_INDEXES):
        op.drop_index(index_name, table_name="surgery_cases")

    _restore_legacy_drug_indexes()
