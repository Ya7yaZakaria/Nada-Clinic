from datetime import date

from app import create_app
from app.extensions import db
from app.models import Patient, User
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_user(email, phone, role_name, name="Test User"):
    user = User(email=email, phone=phone, name=name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)

    return user


def login(client, email):
    return client.post(
        "/auth/login",
        data={
            "login_identifier": email,
            "password": "12345678",
        },
        follow_redirects=True,
    )


def create_patient(**overrides):
    data = {
        "name_ar": "سارة أحمد",
        "name_en": "Sara Ahmed",
        "phone_primary": "01000000000",
        "date_of_birth": date(1996, 7, 1),
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return PatientService.create_patient(**data)


def post_appointment_form(client, patient, **overrides):
    data = {
        "patient_id": str(patient.id),
        "appointment_date": "2026-07-07",
        "appointment_time": "09:30",
        "duration_minutes": "20",
        "appointment_type": Appointment.TYPE_NEW_CONSULTATION,
        "source": Appointment.SOURCE_CLINIC,
        "notes": "First booking",
    }
    data.update(overrides)

    return client.post("/appointments/new", data=data, follow_redirects=True)


def test_appointment_list_requires_login():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.get("/appointments/")

        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]

        db.drop_all()


def test_reception_can_create_appointment():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01020000001", "Reception", "Reception User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = post_appointment_form(client, patient)

        appointment = Appointment.query.first()

        assert response.status_code == 200
        assert appointment is not None
        assert appointment.patient_id == patient.id
        assert appointment.appointment_type == Appointment.TYPE_NEW_CONSULTATION
        assert appointment.status == Appointment.STATUS_BOOKED
        assert patient.visits.count() == 0

        db.drop_all()


def test_appointment_can_be_created_from_patient_workspace_route():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01020000002", "Reception", "Reception User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/appointments/new",
                data={
                    "patient_id": str(patient.id),
                    "appointment_date": "2026-07-08",
                    "appointment_time": "10:00",
                    "duration_minutes": "20",
                    "appointment_type": Appointment.TYPE_FOLLOW_UP,
                    "source": Appointment.SOURCE_PHONE,
                    "notes": "Follow up booking",
                },
                follow_redirects=True,
            )

        appointment = Appointment.query.first()

        assert response.status_code == 200
        assert appointment is not None
        assert appointment.patient_id == patient.id
        assert appointment.appointment_type == Appointment.TYPE_FOLLOW_UP
        assert patient.visits.count() == 0

        db.drop_all()


def test_appointment_can_be_edited():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01020000003", "Reception", "Reception User")
        patient = create_patient()
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date(2026, 7, 7),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.post(
                f"/appointments/{appointment.uuid}/edit",
                data={
                    "patient_id": str(patient.id),
                    "appointment_date": "2026-07-09",
                    "appointment_time": "11:00",
                    "duration_minutes": "30",
                    "appointment_type": Appointment.TYPE_EMERGENCY,
                    "source": Appointment.SOURCE_WHATSAPP,
                    "notes": "Updated booking",
                },
                follow_redirects=True,
            )

        updated = db.session.get(Appointment, appointment.id)

        assert response.status_code == 200
        assert updated.appointment_date == date(2026, 7, 9)
        assert updated.appointment_type == Appointment.TYPE_EMERGENCY
        assert updated.source == Appointment.SOURCE_WHATSAPP
        assert updated.notes == "Updated booking"

        db.drop_all()


def test_patient_appointment_list_works():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01020000004", "Doctor", "Doctor User")
        patient = create_patient()
        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date(2026, 7, 7),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
        )

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/{patient.uuid}/appointments")

        assert response.status_code == 200
        assert b"Sara Ahmed" in response.data
        assert b"MRN 000001" in response.data

        db.drop_all()
