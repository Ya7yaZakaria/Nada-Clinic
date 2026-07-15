"""add partner and prescription targets

Revision ID: 20260715_0068
Revises: 20260715_0067
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa


revision = "20260715_0068"
down_revision = "20260715_0067"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "partners",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("age_years", sa.Integer(), nullable=True),
        sa.Column("occupation", sa.String(length=160), nullable=True),
        sa.Column("previous_children", sa.Text(), nullable=True),
        sa.Column("fertility_notes", sa.Text(), nullable=True),
        sa.Column("medical_notes", sa.Text(), nullable=True),
        sa.Column("follow_up_note", sa.Text(), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_partners_uuid", "partners", ["uuid"], unique=True)
    op.create_index("ix_partners_patient_id", "partners", ["patient_id"])
    op.create_index("ix_partners_is_active", "partners", ["is_active"])
    op.create_index("ix_partners_follow_up_date", "partners", ["follow_up_date"])

    op.create_table(
        "partner_semen_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.Integer(), sa.ForeignKey("partners.id"), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("patient_documents.id"), nullable=True),
        sa.Column("analysis_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_partner_semen_analyses_uuid", "partner_semen_analyses", ["uuid"], unique=True)
    op.create_index("ix_partner_semen_analyses_partner_id", "partner_semen_analyses", ["partner_id"])
    op.create_index("ix_partner_semen_analyses_patient_id", "partner_semen_analyses", ["patient_id"])
    op.create_index("ix_partner_semen_analyses_document_id", "partner_semen_analyses", ["document_id"])
    op.create_index("ix_partner_semen_analyses_analysis_date", "partner_semen_analyses", ["analysis_date"])
    op.create_index("ix_partner_semen_analyses_created_by_user_id", "partner_semen_analyses", ["created_by_user_id"])
    op.create_index("ix_partner_semen_analyses_is_active", "partner_semen_analyses", ["is_active"])

    with op.batch_alter_table("prescriptions") as batch_op:
        batch_op.add_column(sa.Column("prescription_target", sa.String(length=40), nullable=False, server_default="patient"))
        batch_op.add_column(sa.Column("partner_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_prescriptions_partner_id_partners", "partners", ["partner_id"], ["id"])
        batch_op.create_index("ix_prescriptions_prescription_target", ["prescription_target"])
        batch_op.create_index("ix_prescriptions_partner_id", ["partner_id"])
        batch_op.alter_column("visit_id", existing_type=sa.Integer(), nullable=True)

    op.execute("UPDATE prescriptions SET prescription_target = 'patient' WHERE prescription_target IS NULL")


def downgrade():
    with op.batch_alter_table("prescriptions") as batch_op:
        batch_op.alter_column("visit_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_index("ix_prescriptions_partner_id")
        batch_op.drop_index("ix_prescriptions_prescription_target")
        batch_op.drop_constraint("fk_prescriptions_partner_id_partners", type_="foreignkey")
        batch_op.drop_column("partner_id")
        batch_op.drop_column("prescription_target")

    op.drop_index("ix_partner_semen_analyses_is_active", table_name="partner_semen_analyses")
    op.drop_index("ix_partner_semen_analyses_created_by_user_id", table_name="partner_semen_analyses")
    op.drop_index("ix_partner_semen_analyses_analysis_date", table_name="partner_semen_analyses")
    op.drop_index("ix_partner_semen_analyses_document_id", table_name="partner_semen_analyses")
    op.drop_index("ix_partner_semen_analyses_patient_id", table_name="partner_semen_analyses")
    op.drop_index("ix_partner_semen_analyses_partner_id", table_name="partner_semen_analyses")
    op.drop_index("ix_partner_semen_analyses_uuid", table_name="partner_semen_analyses")
    op.drop_table("partner_semen_analyses")

    op.drop_index("ix_partners_follow_up_date", table_name="partners")
    op.drop_index("ix_partners_is_active", table_name="partners")
    op.drop_index("ix_partners_patient_id", table_name="partners")
    op.drop_index("ix_partners_uuid", table_name="partners")
    op.drop_table("partners")
