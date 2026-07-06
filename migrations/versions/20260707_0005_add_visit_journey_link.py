"""add visit journey link

Revision ID: 20260707_0005
Revises: 20260707_0004
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260707_0005"
down_revision = "20260707_0004"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("visits") as batch_op:
        batch_op.add_column(sa.Column("journey_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_visits_journey_id_journeys",
            "journeys",
            ["journey_id"],
            ["id"],
        )
        batch_op.create_index("ix_visits_journey_id", ["journey_id"])


def downgrade():
    with op.batch_alter_table("visits") as batch_op:
        batch_op.drop_index("ix_visits_journey_id")
        batch_op.drop_constraint("fk_visits_journey_id_journeys", type_="foreignkey")
        batch_op.drop_column("journey_id")
