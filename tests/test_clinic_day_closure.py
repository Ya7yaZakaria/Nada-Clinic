from datetime import date

import pytest
from werkzeug.exceptions import Conflict

from app import create_app
from app.extensions import db
from app.models import Appointment, Patient
from app.services.appointment_service import AppointmentService
from app.services.clinic_day_service import ClinicDayService
from app.services.clinic_day_state_service import (
    ClinicDayStateService,
)
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
    )
    return app


def create_patient(number):
    patient = Patient(
        medical_file_number=number,
        name_ar="Closure Patient",
        name_en="Closure Patient",
        search_name="closure patient",
        gender="female",
        phone_primary=f"010{number}",
    )

    db.session.add(patient)
    db.session.commit()

    return patient


def test_closed_day_blocks_appointment_mutations():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(99101)

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=(
                Appointment.TYPE_FOLLOW_UP
            ),
        )

        state = ClinicDayStateService.close_day(
            date.today()
        )

        assert state.is_closed is True
        assert state.closed_at is not None

        with pytest.raises(
            Conflict,
            match="Clinic day is closed",
        ):
            AppointmentService.mark_arrived(
                appointment
            )

        with pytest.raises(
            Conflict,
            match="Clinic day is closed",
        ):
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_EMERGENCY
                ),
            )

        ClinicDayStateService.reopen_day(
            date.today()
        )

        AppointmentService.mark_arrived(
            appointment
        )

        assert (
            appointment.status
            == Appointment.STATUS_ARRIVED
        )

        db.drop_all()


def test_reopen_permission_is_doctor_and_admin_only():
    assert (
        "clinic_day.reopen"
        in RBACService.ROLE_PERMISSION_MATRIX["Doctor"]
    )

    assert (
        "clinic_day.reopen"
        in RBACService.ROLE_PERMISSION_MATRIX["Admin"]
    )

    assert (
        "clinic_day.reopen"
        not in RBACService
        .ROLE_PERMISSION_MATRIX["Reception"]
    )


def test_closing_summary_uses_current_day_totals():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(99102)

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=(
                Appointment.TYPE_NEW_CONSULTATION
            ),
        )

        AppointmentService.mark_no_show(
            appointment
        )

        clinic_day = (
            AppointmentService.get_clinic_day(
                date.today()
            )
        )

        visit_snapshot = (
            ClinicDayService.get_visit_snapshot(
                date.today()
            )
        )

        summary = (
            ClinicDayService.build_closing_summary(
                clinic_day,
                visit_snapshot,
            )
        )

        assert summary["appointments_total"] == 1
        assert summary["no_show_count"] == 1
        assert (
            len(summary["no_show_appointments"])
            == 1
        )

        db.drop_all()