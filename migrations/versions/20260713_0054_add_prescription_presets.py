"""add prescription presets

Revision ID: 20260713_0054
Revises: 20260713_0053
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_0054"
down_revision = "20260713_0053"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "prescription_presets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_index(op.f("ix_prescription_presets_created_by_user_id"), "prescription_presets", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_prescription_presets_is_active"), "prescription_presets", ["is_active"], unique=False)
    op.create_index(op.f("ix_prescription_presets_name"), "prescription_presets", ["name"], unique=True)
    op.create_index(op.f("ix_prescription_presets_updated_by_user_id"), "prescription_presets", ["updated_by_user_id"], unique=False)
    op.create_index(op.f("ix_prescription_presets_uuid"), "prescription_presets", ["uuid"], unique=True)

    op.create_table(
        "prescription_preset_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("preset_id", sa.Integer(), nullable=False),
        sa.Column("drug_id", sa.Integer(), nullable=False),
        sa.Column("dose", sa.String(length=120), nullable=False),
        sa.Column("frequency", sa.String(length=120), nullable=False),
        sa.Column("duration", sa.String(length=120), nullable=False),
        sa.Column("instructions_ar", sa.Text(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["drug_id"], ["drugs.id"]),
        sa.ForeignKeyConstraint(["preset_id"], ["prescription_presets.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["drug_routes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_index(op.f("ix_prescription_preset_items_drug_id"), "prescription_preset_items", ["drug_id"], unique=False)
    op.create_index(op.f("ix_prescription_preset_items_preset_id"), "prescription_preset_items", ["preset_id"], unique=False)
    op.create_index(op.f("ix_prescription_preset_items_route_id"), "prescription_preset_items", ["route_id"], unique=False)
    op.create_index(op.f("ix_prescription_preset_items_sort_order"), "prescription_preset_items", ["sort_order"], unique=False)
    op.create_index(op.f("ix_prescription_preset_items_uuid"), "prescription_preset_items", ["uuid"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_prescription_preset_items_uuid"), table_name="prescription_preset_items")
    op.drop_index(op.f("ix_prescription_preset_items_sort_order"), table_name="prescription_preset_items")
    op.drop_index(op.f("ix_prescription_preset_items_route_id"), table_name="prescription_preset_items")
    op.drop_index(op.f("ix_prescription_preset_items_preset_id"), table_name="prescription_preset_items")
    op.drop_index(op.f("ix_prescription_preset_items_drug_id"), table_name="prescription_preset_items")
    op.drop_table("prescription_preset_items")

    op.drop_index(op.f("ix_prescription_presets_uuid"), table_name="prescription_presets")
    op.drop_index(op.f("ix_prescription_presets_updated_by_user_id"), table_name="prescription_presets")
    op.drop_index(op.f("ix_prescription_presets_name"), table_name="prescription_presets")
    op.drop_index(op.f("ix_prescription_presets_is_active"), table_name="prescription_presets")
    op.drop_index(op.f("ix_prescription_presets_created_by_user_id"), table_name="prescription_presets")
    op.drop_table("prescription_presets")
