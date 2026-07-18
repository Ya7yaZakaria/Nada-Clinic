import importlib.util
from datetime import date, datetime, timezone
from pathlib import Path

import pytest
import sqlalchemy as sa


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "migrations"
    / "versions"
    / "20260719_0070_link_visits_to_appointments.py"
)


def load_migration():
    spec = importlib.util.spec_from_file_location(
        "migration_0070_under_test",
        MIGRATION_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def legacy_database(*, appointment_overrides=None, visits=None, duplicate_appointment=False):
    engine = sa.create_engine("sqlite://")
    metadata = sa.MetaData()
    appointments = sa.Table(
        "appointments",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.Integer, nullable=False),
        sa.Column("appointment_date", sa.Date, nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("arrived_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
    )
    visit_table = sa.Table(
        "visits",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.Integer, nullable=False),
        sa.Column("visit_date", sa.DateTime, nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("completed_at", sa.DateTime),
    )
    metadata.create_all(engine)
    now = datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc)
    appointment = {
        "id": 1,
        "patient_id": 10,
        "appointment_date": date(2026, 7, 1),
        "status": "completed",
        "arrived_at": None,
        "completed_at": now,
    }
    appointment.update(appointment_overrides or {})
    visit_rows = visits if visits is not None else [
        {
            "id": 1,
            "patient_id": 10,
            "visit_date": now,
            "status": "completed",
            "completed_at": now,
        }
    ]
    with engine.begin() as connection:
        connection.execute(appointments.insert(), [appointment])
        if duplicate_appointment:
            second = dict(appointment)
            second["id"] = 2
            connection.execute(appointments.insert(), [second])
        if visit_rows:
            connection.execute(visit_table.insert(), visit_rows)
    return engine


class ValidationOnlyOp:
    def __init__(self, connection):
        self.connection = connection
        self.ddl_started = False

    def get_bind(self):
        return self.connection

    def batch_alter_table(self, _table_name):
        self.ddl_started = True
        raise AssertionError("DDL started before validation completed")


@pytest.mark.parametrize(
    ("appointment_overrides", "visits", "duplicate_appointment", "message"),
    [
        ({"completed_at": None}, None, False, "completed_at is missing"),
        ({}, [], False, "expected exactly one same-day Visit"),
        (
            {},
            [
                {
                    "id": 1,
                    "patient_id": 10,
                    "visit_date": datetime(2026, 7, 1, 9, 0),
                    "status": "completed",
                    "completed_at": datetime(2026, 7, 1, 9, 30),
                },
                {
                    "id": 2,
                    "patient_id": 10,
                    "visit_date": datetime(2026, 7, 1, 11, 0),
                    "status": "completed",
                    "completed_at": datetime(2026, 7, 1, 11, 30),
                },
            ],
            False,
            "expected exactly one same-day Visit",
        ),
        (
            {},
            [
                {
                    "id": 1,
                    "patient_id": 10,
                    "visit_date": datetime(2026, 7, 1, 9, 0),
                    "status": "open",
                    "completed_at": None,
                }
            ],
            False,
            "matching Visit is not completed",
        ),
        (
            {},
            [
                {
                    "id": 1,
                    "patient_id": 10,
                    "visit_date": datetime(2026, 7, 1, 9, 0),
                    "status": "completed",
                    "completed_at": None,
                }
            ],
            False,
            "matching Visit completed_at is missing",
        ),
        ({}, None, True, "matching Visit is reused"),
    ],
)
def test_invalid_legacy_data_aborts_before_sqlite_ddl(
    appointment_overrides,
    visits,
    duplicate_appointment,
    message,
):
    migration = load_migration()
    engine = legacy_database(
        appointment_overrides=appointment_overrides,
        visits=visits,
        duplicate_appointment=duplicate_appointment,
    )
    with engine.connect() as connection:
        fake_op = ValidationOnlyOp(connection)
        migration.op = fake_op
        with pytest.raises(RuntimeError, match=message):
            migration.upgrade()
        assert fake_op.ddl_started is False
        columns = {
            column["name"]
            for column in sa.inspect(connection).get_columns("visits")
        }
        assert "appointment_id" not in columns
