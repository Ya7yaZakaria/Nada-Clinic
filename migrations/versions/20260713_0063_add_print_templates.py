"""add print templates

Revision ID: 20260713_0063
Revises: 20260713_0062
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_0063"
down_revision = "20260713_0062"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "print_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("paper_width_mm", sa.Float(), nullable=False),
        sa.Column("paper_height_mm", sa.Float(), nullable=False),
        sa.Column("layout_json", sa.JSON(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_type", "name", name="uq_print_templates_document_type_name"),
    )

    op.create_index(op.f("ix_print_templates_uuid"), "print_templates", ["uuid"], unique=True)
    op.create_index(op.f("ix_print_templates_name"), "print_templates", ["name"], unique=False)
    op.create_index(op.f("ix_print_templates_document_type"), "print_templates", ["document_type"], unique=False)
    op.create_index(op.f("ix_print_templates_is_default"), "print_templates", ["is_default"], unique=False)
    op.create_index(op.f("ix_print_templates_is_active"), "print_templates", ["is_active"], unique=False)
    op.create_index(op.f("ix_print_templates_created_by_user_id"), "print_templates", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_print_templates_updated_by_user_id"), "print_templates", ["updated_by_user_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_print_templates_updated_by_user_id"), table_name="print_templates")
    op.drop_index(op.f("ix_print_templates_created_by_user_id"), table_name="print_templates")
    op.drop_index(op.f("ix_print_templates_is_active"), table_name="print_templates")
    op.drop_index(op.f("ix_print_templates_is_default"), table_name="print_templates")
    op.drop_index(op.f("ix_print_templates_document_type"), table_name="print_templates")
    op.drop_index(op.f("ix_print_templates_name"), table_name="print_templates")
    op.drop_index(op.f("ix_print_templates_uuid"), table_name="print_templates")
    op.drop_table("print_templates")
