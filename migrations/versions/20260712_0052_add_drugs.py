"""add drugs

Revision ID: 20260712_0052
Revises: 20260712_0051
Create Date: 2026-07-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260712_0052"
down_revision = "20260712_0051"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "drugs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("generic_name", sa.String(length=160), nullable=False),
        sa.Column("trade_name", sa.String(length=160), nullable=False),
        sa.Column("strength", sa.String(length=80), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("form_id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=True),
        sa.Column("pregnancy_status_id", sa.Integer(), nullable=True),
        sa.Column("pregnancy_note", sa.Text(), nullable=True),
        sa.Column("lactation_status_id", sa.Integer(), nullable=True),
        sa.Column("lactation_note", sa.Text(), nullable=True),
        sa.Column("doctor_notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["drug_categories.id"]),
        sa.ForeignKeyConstraint(["form_id"], ["drug_forms.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["drug_routes.id"]),
        sa.ForeignKeyConstraint(["pregnancy_status_id"], ["drug_safety_statuses.id"]),
        sa.ForeignKeyConstraint(["lactation_status_id"], ["drug_safety_statuses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trade_name", "form_id", "strength", name="uq_drugs_trade_form_strength"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_index(op.f("ix_drugs_category_id"), "drugs", ["category_id"], unique=False)
    op.create_index(op.f("ix_drugs_form_id"), "drugs", ["form_id"], unique=False)
    op.create_index(op.f("ix_drugs_generic_name"), "drugs", ["generic_name"], unique=False)
    op.create_index(op.f("ix_drugs_is_active"), "drugs", ["is_active"], unique=False)
    op.create_index(op.f("ix_drugs_lactation_status_id"), "drugs", ["lactation_status_id"], unique=False)
    op.create_index(op.f("ix_drugs_pregnancy_status_id"), "drugs", ["pregnancy_status_id"], unique=False)
    op.create_index(op.f("ix_drugs_route_id"), "drugs", ["route_id"], unique=False)
    op.create_index(op.f("ix_drugs_strength"), "drugs", ["strength"], unique=False)
    op.create_index(op.f("ix_drugs_trade_name"), "drugs", ["trade_name"], unique=False)
    op.create_index(op.f("ix_drugs_uuid"), "drugs", ["uuid"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_drugs_uuid"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_trade_name"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_strength"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_route_id"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_pregnancy_status_id"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_lactation_status_id"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_is_active"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_generic_name"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_form_id"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_category_id"), table_name="drugs")
    op.drop_table("drugs")
