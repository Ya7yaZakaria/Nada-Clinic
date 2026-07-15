"""add surgery cases

Revision ID: 20260715_0067
Revises: 20260715_0066
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa


revision = "20260715_0067"
down_revision = "20260715_0066"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "surgery_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("source_visit_id", sa.Integer(), nullable=True),
        sa.Column("procedure_name", sa.String(length=160), nullable=False),
        sa.Column("procedure_category", sa.String(length=60), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", sa.String(length=160), nullable=True),
        sa.Column("doctor_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("priority", sa.String(length=40), nullable=False),
        sa.Column("pre_op_note", sa.Text(), nullable=True),
        sa.Column("surgery_note", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("operative_findings", sa.Text(), nullable=True),
        sa.Column("operative_details", sa.Text(), nullable=True),
        sa.Column("complications", sa.Text(), nullable=True),
        sa.Column("post_op_plan", sa.Text(), nullable=True),
        sa.Column("fee_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("payment_status", sa.String(length=40), nullable=True),
        sa.Column("cancel_reason", sa.Text(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_by_user_id", sa.Integer(), nullable=True),
        sa.Column("postponed_reason", sa.Text(), nullable=True),
        sa.Column("postponed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("postponed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("rescheduled_from_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("completed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["cancelled_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["completed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["postponed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["source_visit_id"], ["visits.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_surgery_cases_uuid"), "surgery_cases", ["uuid"], unique=True)
    op.create_index(op.f("ix_surgery_cases_patient_id"), "surgery_cases", ["patient_id"], unique=False)
    op.create_index(op.f("ix_surgery_cases_source_visit_id"), "surgery_cases", ["source_visit_id"], unique=False)
    op.create_index(op.f("ix_surgery_cases_scheduled_at"), "surgery_cases", ["scheduled_at"], unique=False)
    op.create_index(op.f("ix_surgery_cases_status"), "surgery_cases", ["status"], unique=False)
    op.create_index(op.f("ix_surgery_cases_procedure_category"), "surgery_cases", ["procedure_category"], unique=False)
    op.create_index(op.f("ix_surgery_cases_is_active"), "surgery_cases", ["is_active"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_surgery_cases_is_active"), table_name="surgery_cases")
    op.drop_index(op.f("ix_surgery_cases_procedure_category"), table_name="surgery_cases")
    op.drop_index(op.f("ix_surgery_cases_status"), table_name="surgery_cases")
    op.drop_index(op.f("ix_surgery_cases_scheduled_at"), table_name="surgery_cases")
    op.drop_index(op.f("ix_surgery_cases_source_visit_id"), table_name="surgery_cases")
    op.drop_index(op.f("ix_surgery_cases_patient_id"), table_name="surgery_cases")
    op.drop_index(op.f("ix_surgery_cases_uuid"), table_name="surgery_cases")
    op.drop_table("surgery_cases")
