"""add patient documents

Revision ID: 20260713_0064
Revises: 20260713_0063
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_0064"
down_revision = "20260713_0063"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "patient_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("visit_id", sa.Integer(), nullable=True),
        sa.Column("investigation_result_id", sa.Integer(), nullable=True),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=160), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("uploaded_by_user_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_result_id"], ["investigation_results.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["visit_id"], ["visits.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_filename", name="uq_patient_documents_stored_filename"),
    )

    op.create_index(op.f("ix_patient_documents_uuid"), "patient_documents", ["uuid"], unique=True)
    op.create_index(op.f("ix_patient_documents_patient_id"), "patient_documents", ["patient_id"], unique=False)
    op.create_index(op.f("ix_patient_documents_visit_id"), "patient_documents", ["visit_id"], unique=False)
    op.create_index(op.f("ix_patient_documents_investigation_result_id"), "patient_documents", ["investigation_result_id"], unique=False)
    op.create_index(op.f("ix_patient_documents_document_type"), "patient_documents", ["document_type"], unique=False)
    op.create_index(op.f("ix_patient_documents_checksum"), "patient_documents", ["checksum"], unique=False)
    op.create_index(op.f("ix_patient_documents_uploaded_by_user_id"), "patient_documents", ["uploaded_by_user_id"], unique=False)
    op.create_index(op.f("ix_patient_documents_is_active"), "patient_documents", ["is_active"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_patient_documents_is_active"), table_name="patient_documents")
    op.drop_index(op.f("ix_patient_documents_uploaded_by_user_id"), table_name="patient_documents")
    op.drop_index(op.f("ix_patient_documents_checksum"), table_name="patient_documents")
    op.drop_index(op.f("ix_patient_documents_document_type"), table_name="patient_documents")
    op.drop_index(op.f("ix_patient_documents_investigation_result_id"), table_name="patient_documents")
    op.drop_index(op.f("ix_patient_documents_visit_id"), table_name="patient_documents")
    op.drop_index(op.f("ix_patient_documents_patient_id"), table_name="patient_documents")
    op.drop_index(op.f("ix_patient_documents_uuid"), table_name="patient_documents")
    op.drop_table("patient_documents")
