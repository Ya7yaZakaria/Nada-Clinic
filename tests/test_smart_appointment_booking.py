from datetime import date

from app import create_app
from app.extensions import db
from app.models import Patient, User
from app.models.appointment import Appointment
from app.models.finance import FinanceCharge
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_reception():
    user = User(
        email="smart-booking@example.com",
        phone="01070000001",
        name="Smart Booking Reception",
    )
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()
    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, "Reception")
    return user


def login(client):
    return client.post(
        "/auth/login",
        data={
            "login_identifier": "smart-booking@example.com",
            "password": "12345678",
        },
    )


def new_patient_data(**overrides):
    data = {
        "patient_mode": "new",
        "patient_id": "",
        "new_patient_name_ar": "سلمى محمود",
        "new_patient_name_en": "Salma Mahmoud",
        "new_patient_phone_primary": "01070000002",
        "new_patient_phone_secondary": "",
        "new_patient_email": "",
        "new_patient_date_of_birth": "1995-04-12",
        "new_patient_age_years_at_registration": "",
        "new_patient_marital_status": "married",
        "new_patient_occupation": "",
        "new_patient_governorate": "",
        "new_patient_city": "",
        "new_patient_street": "",
    }
    data.update(overrides)
    return data


def test_book_appointment_can_register_new_patient_inline():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_reception()

        with app.test_client() as client:
            login(client)
            payload = new_patient_data(
                appointment_date=date.today().isoformat(),
                appointment_time="10:15",
                appointment_type=Appointment.TYPE_NEW_CONSULTATION,
                source=Appointment.SOURCE_PHONE,
                fee_amount="350",
                paid_amount="150",
                payment_method="cash",
                notes="Registered while booking",
            )
            response = client.post(
                "/appointments/new",
                data=payload,
                follow_redirects=True,
            )

        patient = Patient.query.filter_by(name_en="Salma Mahmoud").one()
        appointment = Appointment.query.filter_by(patient_id=patient.id).one()
        charge = FinanceCharge.query.filter_by(
            source_type=FinanceCharge.SOURCE_APPOINTMENT,
            source_id=appointment.id,
        ).one()

        assert response.status_code == 200
        assert appointment.status == Appointment.STATUS_BOOKED
        assert appointment.appointment_type == Appointment.TYPE_NEW_CONSULTATION
        assert charge.gross_amount == 350
        assert charge.paid_amount == 150
        db.drop_all()


def test_emergency_modal_registers_patient_and_adds_complete_booking_to_waiting():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_reception()

        with app.test_client() as client:
            login(client)
            payload = new_patient_data(
                new_patient_name_en="Mona Emergency",
                new_patient_phone_primary="01070000003",
                fee_amount="500",
                paid_amount="500",
                payment_method="cash",
                notes="Urgent pain",
            )
            response = client.post(
                "/appointments/emergency",
                data=payload,
                headers={"HX-Request": "true"},
            )

        patient = Patient.query.filter_by(name_en="Mona Emergency").one()
        appointment = Appointment.query.filter_by(patient_id=patient.id).one()
        charge = FinanceCharge.query.filter_by(
            source_type=FinanceCharge.SOURCE_APPOINTMENT,
            source_id=appointment.id,
        ).one()

        assert response.status_code == 204
        assert appointment.appointment_date == date.today()
        assert appointment.appointment_time is not None
        assert appointment.appointment_time.second == 0
        assert appointment.appointment_type == Appointment.TYPE_EMERGENCY
        assert appointment.source == Appointment.SOURCE_EMERGENCY_UNSCHEDULED
        assert appointment.status == Appointment.STATUS_ARRIVED
        assert charge.service_type == FinanceCharge.SERVICE_EMERGENCY
        assert charge.gross_amount == 500
        assert charge.paid_amount == 500
        db.drop_all()


def test_patient_options_search_offers_existing_and_new_paths():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_reception()
        patient = Patient(
            medical_file_number=711,
            name_ar="هبة علي",
            name_en="Heba Ali",
            search_name="هبة علي heba ali",
            gender="female",
            phone_primary="01070000711",
        )
        db.session.add(patient)
        db.session.commit()

        with app.test_client() as client:
            login(client)
            response = client.get(
                "/appointments/patient-options?q=01070000711&selector_id=test-selector"
            )

        assert response.status_code == 200
        assert b"Heba Ali" in response.data
        assert b"MRN 000711" in response.data
        assert b"Create a new patient" in response.data
        db.drop_all()
