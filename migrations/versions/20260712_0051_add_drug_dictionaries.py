"""add drug dictionaries

Revision ID: 20260712_0051
Revises: ecf98d78d1b4
Create Date: 2026-07-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260712_0051"
down_revision = "ecf98d78d1b4"
branch_labels = None
depends_on = None


def _dictionary_columns(include_severity=False):
    columns = [
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name_en", sa.String(length=120), nullable=False),
        sa.Column("name_ar", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
    ]

    if include_severity:
        columns.append(sa.Column("severity_order", sa.Integer(), nullable=False))

    columns.extend(
        [
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code"),
            sa.UniqueConstraint("uuid"),
        ]
    )

    return columns


def _create_dictionary_table(table_name, include_severity=False):
    op.create_table(table_name, *_dictionary_columns(include_severity=include_severity))
    op.create_index(op.f(f"ix_{table_name}_code"), table_name, ["code"], unique=False)
    op.create_index(op.f(f"ix_{table_name}_is_active"), table_name, ["is_active"], unique=False)
    op.create_index(op.f(f"ix_{table_name}_uuid"), table_name, ["uuid"], unique=False)


def _drop_dictionary_table(table_name):
    op.drop_index(op.f(f"ix_{table_name}_uuid"), table_name=table_name)
    op.drop_index(op.f(f"ix_{table_name}_is_active"), table_name=table_name)
    op.drop_index(op.f(f"ix_{table_name}_code"), table_name=table_name)
    op.drop_table(table_name)


def upgrade():
    _create_dictionary_table("drug_categories")
    _create_dictionary_table("drug_forms")
    _create_dictionary_table("drug_routes")
    _create_dictionary_table("drug_safety_statuses", include_severity=True)


def downgrade():
    _drop_dictionary_table("drug_safety_statuses")
    _drop_dictionary_table("drug_routes")
    _drop_dictionary_table("drug_forms")
    _drop_dictionary_table("drug_categories")
