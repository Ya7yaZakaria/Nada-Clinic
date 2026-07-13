"""add investigation presets

Revision ID: 20260713_0062
Revises: 20260713_0061
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_0062"
down_revision = "20260713_0061"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "investigation_presets",
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
    op.create_index(op.f("ix_investigation_presets_created_by_user_id"), "investigation_presets", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_investigation_presets_is_active"), "investigation_presets", ["is_active"], unique=False)
    op.create_index(op.f("ix_investigation_presets_name"), "investigation_presets", ["name"], unique=True)
    op.create_index(op.f("ix_investigation_presets_updated_by_user_id"), "investigation_presets", ["updated_by_user_id"], unique=False)
    op.create_index(op.f("ix_investigation_presets_uuid"), "investigation_presets", ["uuid"], unique=True)

    op.create_table(
        "investigation_preset_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("preset_id", sa.Integer(), nullable=False),
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["preset_id"], ["investigation_presets.id"]),
        sa.ForeignKeyConstraint(["test_id"], ["investigation_tests.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_investigation_preset_items_preset_id"), "investigation_preset_items", ["preset_id"], unique=False)
    op.create_index(op.f("ix_investigation_preset_items_sort_order"), "investigation_preset_items", ["sort_order"], unique=False)
    op.create_index(op.f("ix_investigation_preset_items_test_id"), "investigation_preset_items", ["test_id"], unique=False)
    op.create_index(op.f("ix_investigation_preset_items_uuid"), "investigation_preset_items", ["uuid"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_investigation_preset_items_uuid"), table_name="investigation_preset_items")
    op.drop_index(op.f("ix_investigation_preset_items_test_id"), table_name="investigation_preset_items")
    op.drop_index(op.f("ix_investigation_preset_items_sort_order"), table_name="investigation_preset_items")
    op.drop_index(op.f("ix_investigation_preset_items_preset_id"), table_name="investigation_preset_items")
    op.drop_table("investigation_preset_items")

    op.drop_index(op.f("ix_investigation_presets_uuid"), table_name="investigation_presets")
    op.drop_index(op.f("ix_investigation_presets_updated_by_user_id"), table_name="investigation_presets")
    op.drop_index(op.f("ix_investigation_presets_name"), table_name="investigation_presets")
    op.drop_index(op.f("ix_investigation_presets_is_active"), table_name="investigation_presets")
    op.drop_index(op.f("ix_investigation_presets_created_by_user_id"), table_name="investigation_presets")
    op.drop_table("investigation_presets")
