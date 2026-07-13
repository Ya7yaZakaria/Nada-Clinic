"""add investigation core models

Revision ID: 20260713_0061
Revises: 20260713_0054
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_0061"
down_revision = "20260713_0054"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "investigation_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name_en", sa.String(length=160), nullable=False),
        sa.Column("name_ar", sa.String(length=160), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_investigation_categories_code"), "investigation_categories", ["code"], unique=True)
    op.create_index(op.f("ix_investigation_categories_is_active"), "investigation_categories", ["is_active"], unique=False)
    op.create_index(op.f("ix_investigation_categories_name_ar"), "investigation_categories", ["name_ar"], unique=False)
    op.create_index(op.f("ix_investigation_categories_name_en"), "investigation_categories", ["name_en"], unique=False)
    op.create_index(op.f("ix_investigation_categories_sort_order"), "investigation_categories", ["sort_order"], unique=False)
    op.create_index(op.f("ix_investigation_categories_uuid"), "investigation_categories", ["uuid"], unique=True)

    op.create_table(
        "investigation_tests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name_en", sa.String(length=160), nullable=False),
        sa.Column("name_ar", sa.String(length=160), nullable=True),
        sa.Column("default_unit", sa.String(length=80), nullable=True),
        sa.Column("default_reference_range", sa.String(length=160), nullable=True),
        sa.Column("result_kind", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["investigation_categories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_investigation_tests_category_id"), "investigation_tests", ["category_id"], unique=False)
    op.create_index(op.f("ix_investigation_tests_code"), "investigation_tests", ["code"], unique=True)
    op.create_index(op.f("ix_investigation_tests_is_active"), "investigation_tests", ["is_active"], unique=False)
    op.create_index(op.f("ix_investigation_tests_name_ar"), "investigation_tests", ["name_ar"], unique=False)
    op.create_index(op.f("ix_investigation_tests_name_en"), "investigation_tests", ["name_en"], unique=False)
    op.create_index(op.f("ix_investigation_tests_result_kind"), "investigation_tests", ["result_kind"], unique=False)
    op.create_index(op.f("ix_investigation_tests_sort_order"), "investigation_tests", ["sort_order"], unique=False)
    op.create_index(op.f("ix_investigation_tests_uuid"), "investigation_tests", ["uuid"], unique=True)

    op.create_table(
        "investigation_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("ordered_visit_id", sa.Integer(), nullable=True),
        sa.Column("journey_id", sa.Integer(), nullable=True),
        sa.Column("ordered_by_user_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("priority", sa.String(length=40), nullable=False),
        sa.Column("order_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["journey_id"], ["journeys.id"]),
        sa.ForeignKeyConstraint(["ordered_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["ordered_visit_id"], ["visits.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_investigation_orders_journey_id"), "investigation_orders", ["journey_id"], unique=False)
    op.create_index(op.f("ix_investigation_orders_ordered_by_user_id"), "investigation_orders", ["ordered_by_user_id"], unique=False)
    op.create_index(op.f("ix_investigation_orders_ordered_visit_id"), "investigation_orders", ["ordered_visit_id"], unique=False)
    op.create_index(op.f("ix_investigation_orders_patient_id"), "investigation_orders", ["patient_id"], unique=False)
    op.create_index(op.f("ix_investigation_orders_priority"), "investigation_orders", ["priority"], unique=False)
    op.create_index(op.f("ix_investigation_orders_status"), "investigation_orders", ["status"], unique=False)
    op.create_index(op.f("ix_investigation_orders_uuid"), "investigation_orders", ["uuid"], unique=True)

    op.create_table(
        "investigation_order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("item_notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["investigation_orders.id"]),
        sa.ForeignKeyConstraint(["test_id"], ["investigation_tests.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_investigation_order_items_order_id"), "investigation_order_items", ["order_id"], unique=False)
    op.create_index(op.f("ix_investigation_order_items_sort_order"), "investigation_order_items", ["sort_order"], unique=False)
    op.create_index(op.f("ix_investigation_order_items_status"), "investigation_order_items", ["status"], unique=False)
    op.create_index(op.f("ix_investigation_order_items_test_id"), "investigation_order_items", ["test_id"], unique=False)
    op.create_index(op.f("ix_investigation_order_items_uuid"), "investigation_order_items", ["uuid"], unique=True)

    op.create_table(
        "investigation_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("test_id", sa.Integer(), nullable=False),
        sa.Column("order_item_id", sa.Integer(), nullable=True),
        sa.Column("ordered_visit_id", sa.Integer(), nullable=True),
        sa.Column("result_visit_id", sa.Integer(), nullable=True),
        sa.Column("result_date", sa.Date(), nullable=False),
        sa.Column("lab_name", sa.String(length=160), nullable=True),
        sa.Column("result_value", sa.String(length=160), nullable=True),
        sa.Column("unit", sa.String(length=80), nullable=True),
        sa.Column("reference_range", sa.String(length=160), nullable=True),
        sa.Column("result_text", sa.Text(), nullable=True),
        sa.Column("doctor_comment", sa.Text(), nullable=True),
        sa.Column("abnormal_flag", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("has_attachment", sa.Boolean(), nullable=False),
        sa.Column("attachment_label", sa.String(length=160), nullable=True),
        sa.Column("external_report_reference", sa.String(length=255), nullable=True),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("entered_by_user_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["entered_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["order_item_id"], ["investigation_order_items.id"]),
        sa.ForeignKeyConstraint(["ordered_visit_id"], ["visits.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["result_visit_id"], ["visits.id"]),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["test_id"], ["investigation_tests.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_investigation_results_abnormal_flag"), "investigation_results", ["abnormal_flag"], unique=False)
    op.create_index(op.f("ix_investigation_results_document_id"), "investigation_results", ["document_id"], unique=False)
    op.create_index(op.f("ix_investigation_results_entered_by_user_id"), "investigation_results", ["entered_by_user_id"], unique=False)
    op.create_index(op.f("ix_investigation_results_has_attachment"), "investigation_results", ["has_attachment"], unique=False)
    op.create_index(op.f("ix_investigation_results_lab_name"), "investigation_results", ["lab_name"], unique=False)
    op.create_index(op.f("ix_investigation_results_order_item_id"), "investigation_results", ["order_item_id"], unique=False)
    op.create_index(op.f("ix_investigation_results_ordered_visit_id"), "investigation_results", ["ordered_visit_id"], unique=False)
    op.create_index(op.f("ix_investigation_results_patient_id"), "investigation_results", ["patient_id"], unique=False)
    op.create_index(op.f("ix_investigation_results_result_date"), "investigation_results", ["result_date"], unique=False)
    op.create_index(op.f("ix_investigation_results_result_visit_id"), "investigation_results", ["result_visit_id"], unique=False)
    op.create_index(op.f("ix_investigation_results_reviewed_by_user_id"), "investigation_results", ["reviewed_by_user_id"], unique=False)
    op.create_index(op.f("ix_investigation_results_status"), "investigation_results", ["status"], unique=False)
    op.create_index(op.f("ix_investigation_results_test_id"), "investigation_results", ["test_id"], unique=False)
    op.create_index(op.f("ix_investigation_results_uuid"), "investigation_results", ["uuid"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_investigation_results_uuid"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_test_id"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_status"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_reviewed_by_user_id"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_result_visit_id"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_result_date"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_patient_id"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_ordered_visit_id"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_order_item_id"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_lab_name"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_has_attachment"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_entered_by_user_id"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_document_id"), table_name="investigation_results")
    op.drop_index(op.f("ix_investigation_results_abnormal_flag"), table_name="investigation_results")
    op.drop_table("investigation_results")

    op.drop_index(op.f("ix_investigation_order_items_uuid"), table_name="investigation_order_items")
    op.drop_index(op.f("ix_investigation_order_items_test_id"), table_name="investigation_order_items")
    op.drop_index(op.f("ix_investigation_order_items_status"), table_name="investigation_order_items")
    op.drop_index(op.f("ix_investigation_order_items_sort_order"), table_name="investigation_order_items")
    op.drop_index(op.f("ix_investigation_order_items_order_id"), table_name="investigation_order_items")
    op.drop_table("investigation_order_items")

    op.drop_index(op.f("ix_investigation_orders_uuid"), table_name="investigation_orders")
    op.drop_index(op.f("ix_investigation_orders_status"), table_name="investigation_orders")
    op.drop_index(op.f("ix_investigation_orders_priority"), table_name="investigation_orders")
    op.drop_index(op.f("ix_investigation_orders_patient_id"), table_name="investigation_orders")
    op.drop_index(op.f("ix_investigation_orders_ordered_visit_id"), table_name="investigation_orders")
    op.drop_index(op.f("ix_investigation_orders_ordered_by_user_id"), table_name="investigation_orders")
    op.drop_index(op.f("ix_investigation_orders_journey_id"), table_name="investigation_orders")
    op.drop_table("investigation_orders")

    op.drop_index(op.f("ix_investigation_tests_uuid"), table_name="investigation_tests")
    op.drop_index(op.f("ix_investigation_tests_sort_order"), table_name="investigation_tests")
    op.drop_index(op.f("ix_investigation_tests_result_kind"), table_name="investigation_tests")
    op.drop_index(op.f("ix_investigation_tests_name_en"), table_name="investigation_tests")
    op.drop_index(op.f("ix_investigation_tests_name_ar"), table_name="investigation_tests")
    op.drop_index(op.f("ix_investigation_tests_is_active"), table_name="investigation_tests")
    op.drop_index(op.f("ix_investigation_tests_code"), table_name="investigation_tests")
    op.drop_index(op.f("ix_investigation_tests_category_id"), table_name="investigation_tests")
    op.drop_table("investigation_tests")

    op.drop_index(op.f("ix_investigation_categories_uuid"), table_name="investigation_categories")
    op.drop_index(op.f("ix_investigation_categories_sort_order"), table_name="investigation_categories")
    op.drop_index(op.f("ix_investigation_categories_name_en"), table_name="investigation_categories")
    op.drop_index(op.f("ix_investigation_categories_name_ar"), table_name="investigation_categories")
    op.drop_index(op.f("ix_investigation_categories_is_active"), table_name="investigation_categories")
    op.drop_index(op.f("ix_investigation_categories_code"), table_name="investigation_categories")
    op.drop_table("investigation_categories")
