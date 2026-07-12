"""add prescriptions

Revision ID: 20260713_0053
Revises: 20260712_0052
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_0053"
down_revision = "20260712_0052"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "prescriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("visit_id", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["visit_id"], ["visits.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
        sa.UniqueConstraint("visit_id"),
    )

    op.create_index(op.f("ix_prescriptions_created_by_user_id"), "prescriptions", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_prescriptions_patient_id"), "prescriptions", ["patient_id"], unique=False)
    op.create_index(op.f("ix_prescriptions_updated_by_user_id"), "prescriptions", ["updated_by_user_id"], unique=False)
    op.create_index(op.f("ix_prescriptions_uuid"), "prescriptions", ["uuid"], unique=True)
    op.create_index(op.f("ix_prescriptions_visit_id"), "prescriptions", ["visit_id"], unique=True)

    op.create_table(
        "prescription_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("prescription_id", sa.Integer(), nullable=False),
        sa.Column("drug_id", sa.Integer(), nullable=False),
        sa.Column("dose", sa.String(length=120), nullable=False),
        sa.Column("frequency", sa.String(length=120), nullable=False),
        sa.Column("duration", sa.String(length=120), nullable=False),
        sa.Column("instructions_ar", sa.Text(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["drug_id"], ["drugs.id"]),
        sa.ForeignKeyConstraint(["prescription_id"], ["prescriptions.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["drug_routes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_index(op.f("ix_prescription_items_drug_id"), "prescription_items", ["drug_id"], unique=False)
    op.create_index(op.f("ix_prescription_items_prescription_id"), "prescription_items", ["prescription_id"], unique=False)
    op.create_index(op.f("ix_prescription_items_route_id"), "prescription_items", ["route_id"], unique=False)
    op.create_index(op.f("ix_prescription_items_sort_order"), "prescription_items", ["sort_order"], unique=False)
    op.create_index(op.f("ix_prescription_items_uuid"), "prescription_items", ["uuid"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_prescription_items_uuid"), table_name="prescription_items")
    op.drop_index(op.f("ix_prescription_items_sort_order"), table_name="prescription_items")
    op.drop_index(op.f("ix_prescription_items_route_id"), table_name="prescription_items")
    op.drop_index(op.f("ix_prescription_items_prescription_id"), table_name="prescription_items")
    op.drop_index(op.f("ix_prescription_items_drug_id"), table_name="prescription_items")
    op.drop_table("prescription_items")

    op.drop_index(op.f("ix_prescriptions_visit_id"), table_name="prescriptions")
    op.drop_index(op.f("ix_prescriptions_uuid"), table_name="prescriptions")
    op.drop_index(op.f("ix_prescriptions_updated_by_user_id"), table_name="prescriptions")
    op.drop_index(op.f("ix_prescriptions_patient_id"), table_name="prescriptions")
    op.drop_index(op.f("ix_prescriptions_created_by_user_id"), table_name="prescriptions")
    op.drop_table("prescriptions")
