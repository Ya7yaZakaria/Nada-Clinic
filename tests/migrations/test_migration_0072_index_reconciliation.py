import pytest

pytestmark = pytest.mark.migration

import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa


MIGRATION_PATH = (
    Path(__file__).parents[2]
    / "migrations"
    / "versions"
    / "20260808_0072_reconcile_model_indexes.py"
)

DRUG_UNIQUE_INDEXES = {
    "drug_categories": {"ix_drug_categories_code", "ix_drug_categories_uuid"},
    "drug_forms": {"ix_drug_forms_code", "ix_drug_forms_uuid"},
    "drug_routes": {"ix_drug_routes_code", "ix_drug_routes_uuid"},
    "drug_safety_statuses": {
        "ix_drug_safety_statuses_code",
        "ix_drug_safety_statuses_uuid",
    },
    "drugs": {"ix_drugs_uuid"},
}

SURGERY_INDEXES = {
    "ix_surgery_cases_cancelled_by_user_id",
    "ix_surgery_cases_completed_at",
    "ix_surgery_cases_completed_by_user_id",
    "ix_surgery_cases_created_by_user_id",
    "ix_surgery_cases_doctor_id",
    "ix_surgery_cases_payment_status",
    "ix_surgery_cases_postponed_by_user_id",
    "ix_surgery_cases_priority",
}


def load_migration():
    spec = importlib.util.spec_from_file_location("migration_0072_under_test", MIGRATION_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def legacy_database():
    engine = sa.create_engine("sqlite://")
    metadata = sa.MetaData()

    for table_name in (
        "drug_categories",
        "drug_forms",
        "drug_routes",
        "drug_safety_statuses",
    ):
        table = sa.Table(
            table_name,
            metadata,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("uuid", sa.String(36), nullable=False, unique=True),
            sa.Column("code", sa.String(80), nullable=False, unique=True),
        )
        sa.Index(f"ix_{table_name}_code", table.c.code)
        sa.Index(f"ix_{table_name}_uuid", table.c.uuid)

    drugs = sa.Table(
        "drugs",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(36), nullable=False, unique=True),
    )
    sa.Index("ix_drugs_uuid", drugs.c.uuid)

    sa.Table(
        "surgery_cases",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cancelled_by_user_id", sa.Integer),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("completed_by_user_id", sa.Integer),
        sa.Column("created_by_user_id", sa.Integer),
        sa.Column("doctor_id", sa.Integer),
        sa.Column("payment_status", sa.String(40)),
        sa.Column("postponed_by_user_id", sa.Integer),
        sa.Column("priority", sa.String(40)),
    )

    metadata.create_all(engine)
    return engine


def run_migration(engine, action):
    migration = load_migration()
    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        migration.op = Operations(context)
        getattr(migration, action)()


def named_indexes(engine, table_name):
    return {
        index["name"]: bool(index.get("unique"))
        for index in sa.inspect(engine).get_indexes(table_name)
    }


def test_upgrade_matches_current_model_index_expectations():
    engine = legacy_database()

    run_migration(engine, "upgrade")

    for table_name, expected_unique_indexes in DRUG_UNIQUE_INDEXES.items():
        indexes = named_indexes(engine, table_name)
        for index_name in expected_unique_indexes:
            assert indexes[index_name] is True

    surgery_indexes = named_indexes(engine, "surgery_cases")
    assert SURGERY_INDEXES <= surgery_indexes.keys()
    assert all(surgery_indexes[index_name] is False for index_name in SURGERY_INDEXES)


def test_downgrade_restores_legacy_index_shape():
    engine = legacy_database()
    run_migration(engine, "upgrade")

    run_migration(engine, "downgrade")

    for table_name, legacy_indexes in DRUG_UNIQUE_INDEXES.items():
        indexes = named_indexes(engine, table_name)
        for index_name in legacy_indexes:
            assert indexes[index_name] is False

    surgery_indexes = named_indexes(engine, "surgery_cases")
    assert SURGERY_INDEXES.isdisjoint(surgery_indexes)
