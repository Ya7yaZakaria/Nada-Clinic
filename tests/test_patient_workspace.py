from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
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
        "phone_secondary": "01111111111",
        "email": "sara@example.com",
        "date_of_birth": date(1996, 7, 1),
        "marital_status": "single",
        "is_virgin": True,
        "occupation": "Teacher",
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return PatientService.create_patient(**data)


def test_workspace_header_shows_required_identity_fields():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01030000001", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"Patient Workspace" in response.data
        assert b"MRN 000001" in response.data
        assert b"Sara Ahmed" in response.data
        assert b"Age" in response.data
        assert b"Phone" in response.data
        assert b"01000000000" in response.data
        assert b"Address" in response.data
        assert b"Qalyubia / Benha / Main Street" in response.data

        db.drop_all()


def test_workspace_uses_arabic_name_when_system_language_is_arabic():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        SettingsService.set("localization.language", "ar")
        create_user("doctor@example.com", "01030000002", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/{patient.uuid}")

        assert response.status_code == 200
        assert "سارة أحمد".encode() in response.data

        db.drop_all()


def test_workspace_shows_core_placeholders_only():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01030000003", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"Clinical Snapshot" in response.data
        assert b"No clinical snapshot yet" in response.data
        assert b"Recent Visits" in response.data
        assert b"No visits yet" in response.data
        assert b"New Visit" in response.data
        assert b"Visits" in response.data
        assert b"Edit" in response.data

        db.drop_all()


def test_workspace_does_not_include_real_visit_links_yet():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01030000004", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b'aria-disabled="true"' in response.data
        assert b"New Visit" in response.data

        db.drop_all()


def test_workspace_shows_virgin_check_and_demographics():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01030000005", "Doctor", "Doctor User")
        patient = create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"Virgin" in response.data
        assert b"Teacher" in response.data
        assert b"01111111111" in response.data
        assert b"sara@example.com" in response.data

        db.drop_all()

