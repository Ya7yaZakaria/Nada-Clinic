"""add external ultrasound request upload metadata

Revision ID: 20260715_0066
Revises: 20260714_0065
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa


revision = "20260715_0066"
down_revision = "20260714_0065"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "external_ultrasound_requests",
        sa.Column("request_categories_json", sa.JSON(), nullable=True),
    )
    op.add_column(
        "external_ultrasound_requests",
        sa.Column("request_modalities_json", sa.JSON(), nullable=True),
    )
    op.add_column(
        "external_ultrasound_requests",
        sa.Column("result_note", sa.Text(), nullable=True),
    )


def downgrade():
    with op.batch_alter_table("external_ultrasound_requests") as batch_op:
        batch_op.drop_column("result_note")
        batch_op.drop_column("request_modalities_json")
        batch_op.drop_column("request_categories_json")
