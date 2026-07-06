"""add journeys

Revision ID: 20260707_0004
Revises: 20260707_0003
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260707_0004"
down_revision = "20260707_0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "journeys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("journey_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("end_date_precision", sa.String(length=20), nullable=True),
        sa.Column("outcome", sa.String(length=80), nullable=True),
        sa.Column("outcome_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_journeys_journey_type"), "journeys", ["journey_type"], unique=False)
    op.create_index(op.f("ix_journeys_outcome"), "journeys", ["outcome"], unique=False)
    op.create_index(op.f("ix_journeys_patient_id"), "journeys", ["patient_id"], unique=False)
    op.create_index(op.f("ix_journeys_status"), "journeys", ["status"], unique=False)
    op.create_index(op.f("ix_journeys_uuid"), "journeys", ["uuid"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_journeys_uuid"), table_name="journeys")
    op.drop_index(op.f("ix_journeys_status"), table_name="journeys")
    op.drop_index(op.f("ix_journeys_patient_id"), table_name="journeys")
    op.drop_index(op.f("ix_journeys_outcome"), table_name="journeys")
    op.drop_index(op.f("ix_journeys_journey_type"), table_name="journeys")
    op.drop_table("journeys")
