from datetime import date

from app import create_app
from app.extensions import db
from app.models import Patient, User
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


def get_patient(patient_id):
    return db.session.get(Patient, patient_id)


def post_patient_form(client, **overrides):
    data = {
        "name_ar": "سارة أحمد",
        "name_en": "Sara Ahmed",
        "phone_primary": "01000000000",
        "phone_secondary": "",
        "email": "",
        "date_of_birth": "1996-07-01",
        "age_years_at_registration": "",
        "marital_status": "unknown",
        "occupation": "",
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return client.post("/patients/new", data=data, follow_redirects=True)


def test_anonymous_user_is_blocked_from_patients():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.get("/patients/")

        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]

        db.drop_all()


def test_doctor_can_view_patient_list():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01010000001", "Doctor", "Doctor User")
        create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/patients/")

        assert response.status_code == 200
        assert b"Patients" in response.data
        assert "Sara Ahmed".encode() in response.data

        db.drop_all()


def test_reception_can_create_patient():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01010000002", "Reception", "Reception User")

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = post_patient_form(client)

        patient = Patient.query.filter_by(name_en="Sara Ahmed").first()

        assert response.status_code == 200
        assert patient is not None
        assert patient.formatted_mrn == "000001"
        assert b"MRN 000001" in response.data

        db.drop_all()


def test_patient_create_requires_name_phone_and_age_source():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01010000003", "Reception", "Reception User")

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = post_patient_form(
                client,
                name_ar="",
                phone_primary="",
                date_of_birth="",
                age_years_at_registration="",
            )

        assert response.status_code == 200
        assert Patient.query.count() == 0
        assert b"Arabic name" in response.data

        db.drop_all()


def test_patient_can_be_edited():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01010000004", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/edit",
                data={
                    "name_ar": "سارة محمد",
                    "name_en": "Sara Mohamed",
                    "phone_primary": "01099999999",
                    "phone_secondary": "",
                    "email": "",
                    "date_of_birth": "1996-07-01",
                    "age_years_at_registration": "",
                    "marital_status": "married",
                    "occupation": "Teacher",
                    "governorate": "Cairo",
                    "city": "Nasr City",
                    "street": "Street 9",
                },
                follow_redirects=True,
            )

        updated_patient = get_patient(patient.id)

        assert response.status_code == 200
        assert updated_patient.name_en == "Sara Mohamed"
        assert updated_patient.phone_primary == "01099999999"
        assert updated_patient.marital_status == "married"
        assert b"Sara Mohamed" in response.data

        db.drop_all()


def test_duplicate_phone_is_allowed_with_warning_on_create():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception@example.com", "01010000005", "Reception", "Reception User")
        create_patient(phone_primary="01011111111")

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = post_patient_form(
                client,
                name_ar="منى أحمد",
                name_en="Mona Ahmed",
                phone_primary="01011111111",
            )

        assert response.status_code == 200
        assert Patient.query.count() == 2
        assert b"Warning" in response.data

        db.drop_all()


def test_non_admin_cannot_change_mrn():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01010000006", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/mrn",
                data={
                    "medical_file_number": 10,
                    "confirm_mrn_change": "y",
                },
                follow_redirects=True,
            )

        assert response.status_code == 403
        assert get_patient(patient.id).medical_file_number == 1

        db.drop_all()


def test_admin_can_change_mrn_with_warning_confirmation():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("admin@example.com", "01010000007", "Admin", "Admin User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "admin@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/mrn",
                data={
                    "medical_file_number": 10,
                    "confirm_mrn_change": "y",
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert get_patient(patient.id).medical_file_number == 10
        assert b"MRN 000010" in response.data

        db.drop_all()


def test_admin_mrn_change_requires_confirmation():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("admin@example.com", "01010000008", "Admin", "Admin User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "admin@example.com")
            response = client.post(
                f"/patients/{patient.uuid}/mrn",
                data={
                    "medical_file_number": 10,
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert get_patient(patient.id).medical_file_number == 1
        assert b"MRN change was not confirmed" in response.data

        db.drop_all()


def test_patient_workspace_header_shows_core_identity():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01010000009", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"Patient Workspace" in response.data
        assert b"MRN 000001" in response.data
        assert b"Sara Ahmed" in response.data
        assert b"Age:" in response.data
        assert b"Phone: 01000000000" in response.data
        assert b"New Visit" in response.data
        assert b"Visits" in response.data
        assert b"Edit" in response.data

        db.drop_all()
