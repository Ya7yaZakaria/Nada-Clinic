
from datetime import date

from app import create_app
from app.extensions import db
from app.models import (
    Appointment,
    FinanceCharge,
    FinanceExpense,
    Patient,
    SurgeryCase,
    User,
)
from app.services.demo_data_service import DemoDataService


def make_app(tmp_path):
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        PATIENT_DOCUMENT_UPLOAD_FOLDER=str(
            tmp_path / "patient_documents"
        ),
    )
    return app


def test_seed_demo_creates_five_month_dataset_without_users(
    tmp_path,
):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()

        users_before = User.query.count()

        result = DemoDataService.seed()
        summary = DemoDataService.summary()

        assert result["created"] is True

        assert summary["patients"] == (
            DemoDataService.PATIENT_COUNT
        )

        assert summary["appointments"] == (
            DemoDataService.expected_appointment_count()
        )

        assert summary["visits"] > 300
        assert summary["journeys"] == 180
        assert summary["partners"] >= 25
        assert summary["prescriptions"] >= 40
        assert summary["investigation_results"] >= 40
        assert summary["clinic_ultrasounds"] >= 30
        assert summary["external_ultrasounds"] >= 10
        assert summary["documents"] >= 15
        assert summary["surgeries"] == 28
        assert summary["finance_charges"] > 300
        assert summary["expenses"] >= 25

        assert User.query.count() == users_before

        friday_appointments = Appointment.query.filter(
            db.extract(
                "dow",
                Appointment.appointment_date,
            )
            == 5
        ).count()

        assert friday_appointments == 0

        future_appointments = Appointment.query.filter(
            Appointment.appointment_date > date.today()
        ).all()

        assert future_appointments
        assert all(
            appointment.status
            == Appointment.STATUS_BOOKED
            for appointment in future_appointments
        )

        assert SurgeryCase.query.filter_by(
            status=SurgeryCase.STATUS_COMPLETED
        ).count() > 10

        assert SurgeryCase.query.filter_by(
            status=SurgeryCase.STATUS_SCHEDULED
        ).count() > 0

        assert FinanceCharge.query.count() > 300
        assert FinanceExpense.query.count() >= 25

        db.drop_all()


def test_seed_demo_is_idempotent(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()

        first = DemoDataService.seed()
        first_summary = DemoDataService.summary()

        second = DemoDataService.seed()
        second_summary = DemoDataService.summary()

        assert first["created"] is True
        assert second["created"] is False
        assert second_summary == first_summary
        assert User.query.count() == 0

        db.drop_all()


def test_seed_demo_command_is_registered(tmp_path):
    app = make_app(tmp_path)
    runner = app.test_cli_runner()

    with app.app_context():
        db.create_all()

        result = runner.invoke(
            args=["seed-demo"],
        )

        assert result.exit_code == 0, result.output
        assert (
            "Five-month demo clinic data created."
            in result.output
        )
        assert "Patients: 180" in result.output
        assert "Surgeries: 28" in result.output
        assert "Finance charges:" in result.output
        assert "Expenses:" in result.output
        assert "No users were created." in result.output

        db.drop_all()
