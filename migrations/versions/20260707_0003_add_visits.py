"""add visits

Revision ID: 20260707_0003
Revises: 8361f153ca45
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260707_0003"
down_revision = "8361f153ca45"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "visits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("visit_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("visit_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reopened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("chief_complaint", sa.Text(), nullable=True),
        sa.Column("history", sa.Text(), nullable=True),
        sa.Column("examination", sa.Text(), nullable=True),
        sa.Column("assessment", sa.Text(), nullable=True),
        sa.Column("plan", sa.Text(), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("is_locked", sa.Boolean(), nullable=False),
        sa.Column("completed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("reopened_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["completed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["reopened_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_visits_completed_by_user_id"), "visits", ["completed_by_user_id"], unique=False)
    op.create_index(op.f("ix_visits_patient_id"), "visits", ["patient_id"], unique=False)
    op.create_index(op.f("ix_visits_reopened_by_user_id"), "visits", ["reopened_by_user_id"], unique=False)
    op.create_index(op.f("ix_visits_status"), "visits", ["status"], unique=False)
    op.create_index(op.f("ix_visits_uuid"), "visits", ["uuid"], unique=False)
    op.create_index(op.f("ix_visits_visit_date"), "visits", ["visit_date"], unique=False)
    op.create_index(op.f("ix_visits_visit_type"), "visits", ["visit_type"], unique=False)

    op.create_table(
        "visit_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("visit_id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=True),
        sa.Column("message", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["visit_id"], ["visits.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_visit_audit_logs_action"), "visit_audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_visit_audit_logs_actor_user_id"), "visit_audit_logs", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_visit_audit_logs_created_at"), "visit_audit_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_visit_audit_logs_patient_id"), "visit_audit_logs", ["patient_id"], unique=False)
    op.create_index(op.f("ix_visit_audit_logs_visit_id"), "visit_audit_logs", ["visit_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_visit_audit_logs_visit_id"), table_name="visit_audit_logs")
    op.drop_index(op.f("ix_visit_audit_logs_patient_id"), table_name="visit_audit_logs")
    op.drop_index(op.f("ix_visit_audit_logs_created_at"), table_name="visit_audit_logs")
    op.drop_index(op.f("ix_visit_audit_logs_actor_user_id"), table_name="visit_audit_logs")
    op.drop_index(op.f("ix_visit_audit_logs_action"), table_name="visit_audit_logs")
    op.drop_table("visit_audit_logs")

    op.drop_index(op.f("ix_visits_visit_type"), table_name="visits")
    op.drop_index(op.f("ix_visits_visit_date"), table_name="visits")
    op.drop_index(op.f("ix_visits_uuid"), table_name="visits")
    op.drop_index(op.f("ix_visits_status"), table_name="visits")
    op.drop_index(op.f("ix_visits_reopened_by_user_id"), table_name="visits")
    op.drop_index(op.f("ix_visits_patient_id"), table_name="visits")
    op.drop_index(op.f("ix_visits_completed_by_user_id"), table_name="visits")
    op.drop_table("visits")
