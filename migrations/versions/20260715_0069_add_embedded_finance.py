"""add embedded finance

Revision ID: 20260715_0069
Revises: 20260715_0068
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa


revision = "20260715_0069"
down_revision = "20260715_0068"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "finance_charges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("service_type", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("gross_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("net_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("remaining_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_finance_charges_uuid", "finance_charges", ["uuid"], unique=True)
    op.create_index("ix_finance_charges_patient_id", "finance_charges", ["patient_id"])
    op.create_index("ix_finance_charges_source_type", "finance_charges", ["source_type"])
    op.create_index("ix_finance_charges_source_id", "finance_charges", ["source_id"])
    op.create_index("ix_finance_charges_service_type", "finance_charges", ["service_type"])
    op.create_index("ix_finance_charges_status", "finance_charges", ["status"])
    op.create_index("ix_finance_charges_service_date", "finance_charges", ["service_date"])
    op.create_index("ix_finance_charges_created_by_user_id", "finance_charges", ["created_by_user_id"])
    op.create_index("ix_finance_charges_updated_by_user_id", "finance_charges", ["updated_by_user_id"])
    op.create_index("ix_finance_charges_source", "finance_charges", ["source_type", "source_id"])
    op.create_index("ix_finance_charges_date_service", "finance_charges", ["service_date", "service_type"])

    op.create_table(
        "finance_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("charge_id", sa.Integer(), sa.ForeignKey("finance_charges.id"), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_finance_payments_uuid", "finance_payments", ["uuid"], unique=True)
    op.create_index("ix_finance_payments_patient_id", "finance_payments", ["patient_id"])
    op.create_index("ix_finance_payments_charge_id", "finance_payments", ["charge_id"])
    op.create_index("ix_finance_payments_payment_date", "finance_payments", ["payment_date"])
    op.create_index("ix_finance_payments_payment_method", "finance_payments", ["payment_method"])
    op.create_index("ix_finance_payments_created_by_user_id", "finance_payments", ["created_by_user_id"])

    op.create_table(
        "finance_expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", sa.String(length=40), nullable=False),
        sa.Column("vendor_or_staff_name", sa.String(length=180), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_finance_expenses_uuid", "finance_expenses", ["uuid"], unique=True)
    op.create_index("ix_finance_expenses_expense_date", "finance_expenses", ["expense_date"])
    op.create_index("ix_finance_expenses_category", "finance_expenses", ["category"])
    op.create_index("ix_finance_expenses_payment_method", "finance_expenses", ["payment_method"])
    op.create_index("ix_finance_expenses_created_by_user_id", "finance_expenses", ["created_by_user_id"])

    with op.batch_alter_table("appointments") as batch_op:
        batch_op.add_column(sa.Column("fee_amount", sa.Numeric(12, 2), nullable=True))
        batch_op.add_column(sa.Column("paid_amount", sa.Numeric(12, 2), nullable=True))
        batch_op.add_column(sa.Column("payment_method", sa.String(length=40), nullable=True))
        batch_op.create_index("ix_appointments_payment_method", ["payment_method"])

    with op.batch_alter_table("visits") as batch_op:
        batch_op.add_column(sa.Column("billing_service_type", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("fee_amount", sa.Numeric(12, 2), nullable=True))
        batch_op.add_column(sa.Column("paid_amount", sa.Numeric(12, 2), nullable=True))
        batch_op.add_column(sa.Column("payment_method", sa.String(length=40), nullable=True))
        batch_op.create_index("ix_visits_billing_service_type", ["billing_service_type"])
        batch_op.create_index("ix_visits_payment_method", ["payment_method"])

    with op.batch_alter_table("surgery_cases") as batch_op:
        batch_op.add_column(sa.Column("payment_method", sa.String(length=40), nullable=True))
        batch_op.create_index("ix_surgery_cases_payment_method", ["payment_method"])


def downgrade():
    with op.batch_alter_table("surgery_cases") as batch_op:
        batch_op.drop_index("ix_surgery_cases_payment_method")
        batch_op.drop_column("payment_method")

    with op.batch_alter_table("visits") as batch_op:
        batch_op.drop_index("ix_visits_payment_method")
        batch_op.drop_index("ix_visits_billing_service_type")
        batch_op.drop_column("payment_method")
        batch_op.drop_column("paid_amount")
        batch_op.drop_column("fee_amount")
        batch_op.drop_column("billing_service_type")

    with op.batch_alter_table("appointments") as batch_op:
        batch_op.drop_index("ix_appointments_payment_method")
        batch_op.drop_column("payment_method")
        batch_op.drop_column("paid_amount")
        batch_op.drop_column("fee_amount")

    op.drop_index("ix_finance_expenses_created_by_user_id", table_name="finance_expenses")
    op.drop_index("ix_finance_expenses_payment_method", table_name="finance_expenses")
    op.drop_index("ix_finance_expenses_category", table_name="finance_expenses")
    op.drop_index("ix_finance_expenses_expense_date", table_name="finance_expenses")
    op.drop_index("ix_finance_expenses_uuid", table_name="finance_expenses")
    op.drop_table("finance_expenses")

    op.drop_index("ix_finance_payments_created_by_user_id", table_name="finance_payments")
    op.drop_index("ix_finance_payments_payment_method", table_name="finance_payments")
    op.drop_index("ix_finance_payments_payment_date", table_name="finance_payments")
    op.drop_index("ix_finance_payments_charge_id", table_name="finance_payments")
    op.drop_index("ix_finance_payments_patient_id", table_name="finance_payments")
    op.drop_index("ix_finance_payments_uuid", table_name="finance_payments")
    op.drop_table("finance_payments")

    op.drop_index("ix_finance_charges_date_service", table_name="finance_charges")
    op.drop_index("ix_finance_charges_source", table_name="finance_charges")
    op.drop_index("ix_finance_charges_updated_by_user_id", table_name="finance_charges")
    op.drop_index("ix_finance_charges_created_by_user_id", table_name="finance_charges")
    op.drop_index("ix_finance_charges_service_date", table_name="finance_charges")
    op.drop_index("ix_finance_charges_status", table_name="finance_charges")
    op.drop_index("ix_finance_charges_service_type", table_name="finance_charges")
    op.drop_index("ix_finance_charges_source_id", table_name="finance_charges")
    op.drop_index("ix_finance_charges_source_type", table_name="finance_charges")
    op.drop_index("ix_finance_charges_patient_id", table_name="finance_charges")
    op.drop_index("ix_finance_charges_uuid", table_name="finance_charges")
    op.drop_table("finance_charges")
