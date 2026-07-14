"""add ultrasound foundation

Revision ID: 20260714_0065
Revises: 20260713_0064
Create Date: 2026-07-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260714_0065"
down_revision = "20260713_0064"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "clinic_ultrasound_exams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("visit_id", sa.Integer(), nullable=False),
        sa.Column("journey_id", sa.Integer(), nullable=True),
        sa.Column("exam_type", sa.String(length=40), nullable=False),
        sa.Column("exam_route", sa.String(length=40), nullable=False),
        sa.Column("findings_json", sa.JSON(), nullable=False),
        sa.Column("findings_text", sa.Text(), nullable=True),
        sa.Column("extra_note", sa.Text(), nullable=True),
        sa.Column("impression", sa.Text(), nullable=True),
        sa.Column("sketch_note", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["journey_id"], ["journeys.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["visit_id"], ["visits.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_clinic_ultrasound_exams_uuid"), "clinic_ultrasound_exams", ["uuid"], unique=True)
    op.create_index(op.f("ix_clinic_ultrasound_exams_patient_id"), "clinic_ultrasound_exams", ["patient_id"], unique=False)
    op.create_index(op.f("ix_clinic_ultrasound_exams_visit_id"), "clinic_ultrasound_exams", ["visit_id"], unique=False)
    op.create_index(op.f("ix_clinic_ultrasound_exams_journey_id"), "clinic_ultrasound_exams", ["journey_id"], unique=False)
    op.create_index(op.f("ix_clinic_ultrasound_exams_exam_type"), "clinic_ultrasound_exams", ["exam_type"], unique=False)
    op.create_index(op.f("ix_clinic_ultrasound_exams_exam_route"), "clinic_ultrasound_exams", ["exam_route"], unique=False)
    op.create_index(op.f("ix_clinic_ultrasound_exams_created_by_user_id"), "clinic_ultrasound_exams", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_clinic_ultrasound_exams_is_active"), "clinic_ultrasound_exams", ["is_active"], unique=False)

    op.create_table(
        "external_ultrasound_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("requested_visit_id", sa.Integer(), nullable=False),
        sa.Column("result_visit_id", sa.Integer(), nullable=True),
        sa.Column("request_note", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("result_document_id", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("completed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["completed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["requested_visit_id"], ["visits.id"]),
        sa.ForeignKeyConstraint(["result_document_id"], ["patient_documents.id"]),
        sa.ForeignKeyConstraint(["result_visit_id"], ["visits.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_external_ultrasound_requests_uuid"), "external_ultrasound_requests", ["uuid"], unique=True)
    op.create_index(op.f("ix_external_ultrasound_requests_patient_id"), "external_ultrasound_requests", ["patient_id"], unique=False)
    op.create_index(op.f("ix_external_ultrasound_requests_requested_visit_id"), "external_ultrasound_requests", ["requested_visit_id"], unique=False)
    op.create_index(op.f("ix_external_ultrasound_requests_result_visit_id"), "external_ultrasound_requests", ["result_visit_id"], unique=False)
    op.create_index(op.f("ix_external_ultrasound_requests_status"), "external_ultrasound_requests", ["status"], unique=False)
    op.create_index(op.f("ix_external_ultrasound_requests_result_document_id"), "external_ultrasound_requests", ["result_document_id"], unique=False)
    op.create_index(op.f("ix_external_ultrasound_requests_created_by_user_id"), "external_ultrasound_requests", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_external_ultrasound_requests_completed_by_user_id"), "external_ultrasound_requests", ["completed_by_user_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_external_ultrasound_requests_completed_by_user_id"), table_name="external_ultrasound_requests")
    op.drop_index(op.f("ix_external_ultrasound_requests_created_by_user_id"), table_name="external_ultrasound_requests")
    op.drop_index(op.f("ix_external_ultrasound_requests_result_document_id"), table_name="external_ultrasound_requests")
    op.drop_index(op.f("ix_external_ultrasound_requests_status"), table_name="external_ultrasound_requests")
    op.drop_index(op.f("ix_external_ultrasound_requests_result_visit_id"), table_name="external_ultrasound_requests")
    op.drop_index(op.f("ix_external_ultrasound_requests_requested_visit_id"), table_name="external_ultrasound_requests")
    op.drop_index(op.f("ix_external_ultrasound_requests_patient_id"), table_name="external_ultrasound_requests")
    op.drop_index(op.f("ix_external_ultrasound_requests_uuid"), table_name="external_ultrasound_requests")
    op.drop_table("external_ultrasound_requests")

    op.drop_index(op.f("ix_clinic_ultrasound_exams_is_active"), table_name="clinic_ultrasound_exams")
    op.drop_index(op.f("ix_clinic_ultrasound_exams_created_by_user_id"), table_name="clinic_ultrasound_exams")
    op.drop_index(op.f("ix_clinic_ultrasound_exams_exam_route"), table_name="clinic_ultrasound_exams")
    op.drop_index(op.f("ix_clinic_ultrasound_exams_exam_type"), table_name="clinic_ultrasound_exams")
    op.drop_index(op.f("ix_clinic_ultrasound_exams_journey_id"), table_name="clinic_ultrasound_exams")
    op.drop_index(op.f("ix_clinic_ultrasound_exams_visit_id"), table_name="clinic_ultrasound_exams")
    op.drop_index(op.f("ix_clinic_ultrasound_exams_patient_id"), table_name="clinic_ultrasound_exams")
    op.drop_index(op.f("ix_clinic_ultrasound_exams_uuid"), table_name="clinic_ultrasound_exams")
    op.drop_table("clinic_ultrasound_exams")
