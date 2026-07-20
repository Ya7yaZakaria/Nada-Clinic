"""add clinic day states

Revision ID: 20260720_0071
Revises: 20260719_0070
Create Date: 2026-07-20
"""

from alembic import op
import sqlalchemy as sa


revision = "20260720_0071"
down_revision = "20260719_0070"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "clinic_day_states",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "uuid",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "clinic_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "is_closed",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "closed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "reopened_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_index(
        "ix_clinic_day_states_clinic_date",
        "clinic_day_states",
        ["clinic_date"],
        unique=True,
    )

    op.create_index(
        "ix_clinic_day_states_is_closed",
        "clinic_day_states",
        ["is_closed"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_clinic_day_states_is_closed",
        table_name="clinic_day_states",
    )

    op.drop_index(
        "ix_clinic_day_states_clinic_date",
        table_name="clinic_day_states",
    )

    op.drop_table("clinic_day_states")