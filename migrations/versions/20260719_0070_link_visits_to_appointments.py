"""link visits to appointments and remove appointment completion

Revision ID: 20260719_0070
Revises: 20260715_0069
"""
from alembic import op
import sqlalchemy as sa


revision = "20260719_0070"
down_revision = "20260715_0069"
branch_labels = None
depends_on = None


def _as_date(value):
    return value.date() if hasattr(value, "date") else value


def upgrade():
    bind = op.get_bind()
    metadata = sa.MetaData()
    appointments = sa.Table("appointments", metadata, autoload_with=bind)
    visits = sa.Table("visits", metadata, autoload_with=bind)
    legacy = bind.execute(sa.select(appointments).where(appointments.c.status == "completed")).mappings().all()
    visit_rows = bind.execute(sa.select(visits)).mappings().all()
    appointment_rows = bind.execute(sa.select(appointments)).mappings().all()
    used_visits = set()
    links = []

    for appointment in legacy:
        if appointment["completed_at"] is None:
            raise RuntimeError(
                f"Cannot safely migrate completed appointment {appointment['id']}: completed_at is missing"
            )

        active_conflicts = [row for row in appointment_rows if row["id"] != appointment["id"] and row["patient_id"] == appointment["patient_id"] and row["appointment_date"] == appointment["appointment_date"] and row["status"] in {"booked", "arrived"}]
        if active_conflicts:
            raise RuntimeError(f"Cannot safely migrate completed appointment {appointment['id']}: same-day active appointment exists")

        matches = [
            row
            for row in visit_rows
            if row["patient_id"] == appointment["patient_id"]
            and _as_date(row["visit_date"]) == appointment["appointment_date"]
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"Cannot safely migrate completed appointment {appointment['id']}: expected exactly one same-day Visit, found {len(matches)}"
            )

        visit = matches[0]
        if visit["status"] != "completed":
            raise RuntimeError(
                f"Cannot safely migrate completed appointment {appointment['id']}: matching Visit is not completed"
            )
        if visit["completed_at"] is None:
            raise RuntimeError(
                f"Cannot safely migrate completed appointment {appointment['id']}: matching Visit completed_at is missing"
            )
        if visit["id"] in used_visits:
            raise RuntimeError(
                f"Cannot safely migrate completed appointment {appointment['id']}: matching Visit is reused"
            )

        used_visits.add(visit["id"])
        links.append((appointment, visit))

    with op.batch_alter_table("visits") as batch_op:
        batch_op.add_column(sa.Column("appointment_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_visits_appointment_id_appointments", "appointments", ["appointment_id"], ["id"])
        batch_op.create_index("ix_visits_appointment_id", ["appointment_id"], unique=True)

    metadata = sa.MetaData()
    appointments = sa.Table("appointments", metadata, autoload_with=bind)
    visits = sa.Table("visits", metadata, autoload_with=bind)

    for appointment, visit in links:
        bind.execute(visits.update().where(visits.c.id == visit["id"]).values(appointment_id=appointment["id"]))
        bind.execute(appointments.update().where(appointments.c.id == appointment["id"]).values(status="arrived", arrived_at=appointment["arrived_at"] or appointment["completed_at"]))

    with op.batch_alter_table("appointments") as batch_op:
        batch_op.drop_column("completed_at")


def downgrade():
    with op.batch_alter_table("appointments") as batch_op:
        batch_op.add_column(sa.Column("completed_at", sa.DateTime(), nullable=True))
    bind = op.get_bind()
    metadata = sa.MetaData()
    appointments = sa.Table("appointments", metadata, autoload_with=bind)
    visits = sa.Table("visits", metadata, autoload_with=bind)
    linked = bind.execute(sa.select(visits).where(visits.c.appointment_id.is_not(None), visits.c.status == "completed")).mappings().all()
    for visit in linked:
        bind.execute(appointments.update().where(appointments.c.id == visit["appointment_id"]).values(status="completed", completed_at=visit["completed_at"]))
    with op.batch_alter_table("visits") as batch_op:
        batch_op.drop_index("ix_visits_appointment_id")
        batch_op.drop_constraint("fk_visits_appointment_id_appointments", type_="foreignkey")
        batch_op.drop_column("appointment_id")
