from tests.factories import login, set_test_password
from tests.factories import make_app_server as make_app

from datetime import date

from app import create_app
from app.extensions import db
from app.models import Appointment, Patient, User
from app.services.appointment_service import AppointmentService
from app.services.rbac_service import RBACService


def test_today_clinic_uses_compact_operational_command_center():
    app = make_app()
    with app.app_context():
        db.create_all()
        user = User(email="today-command@example.com", phone="01077110000", name="Reception")
        set_test_password(user, "12345678")
        db.session.add(user)
        db.session.commit()
        RBACService.seed_roles_permissions()
        RBACService.assign_role(user, "Reception")

        patient = Patient(
            medical_file_number=7711,
            name_ar="Command Patient",
            name_en="Command Patient",
            search_name="command patient",
            gender="female",
            phone_primary="01077117711",
        )
        db.session.add(patient)
        db.session.commit()
        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_EMERGENCY,
        )

        client = app.test_client()
        login(client, user.email)
        response = client.get(f"/clinic/day/{date.today().isoformat()}")

        assert response.status_code == 200
        assert b"Visits Today" not in response.data
        assert b"Cancelled / No-show" in response.data
        assert b"Clinic Pulse" in response.data
        assert b'id="clinic-list-search"' in response.data
        assert b'id="clinic-list-sort"' in response.data
        assert b'data-clinic-quick-filter="emergency"' in response.data
        assert b'data-clinic-patient-card' in response.data
        assert b"Appointment details" in response.data
        assert b"transition:true" in response.data

        db.drop_all()
