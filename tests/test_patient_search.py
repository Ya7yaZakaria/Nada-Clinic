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
        "date_of_birth": date(1996, 7, 1),
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return PatientService.create_patient(**data)


def seed_search_patients():
    first = create_patient(
        name_ar="سارة أحمد",
        name_en="Sara Ahmed",
        phone_primary="01000000001",
    )
    second = create_patient(
        name_ar="منى محمود",
        name_en="Mona Mahmoud",
        phone_primary="01000000002",
    )
    third = create_patient(
        name_ar="ليلى حسن",
        name_en="Laila Hassan",
        phone_primary="01000000001",
        city="Cairo",
    )

    return first, second, third


def test_patient_search_route_requires_login():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.get("/patients/search?q=sara")

        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]

        db.drop_all()


def test_search_by_arabic_name():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01020000001", "Doctor", "Doctor User")
        seed_search_patients()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/patients/search?q=سارة")

        assert response.status_code == 200
        assert "سارة أحمد".encode() in response.data
        assert "منى محمود".encode() not in response.data

        db.drop_all()


def test_search_by_english_name():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01020000002", "Doctor", "Doctor User")
        seed_search_patients()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/patients/search?q=Mona")

        assert response.status_code == 200
        assert b"Mona Mahmoud" in response.data
        assert b"Sara Ahmed" not in response.data

        db.drop_all()


def test_search_by_mrn_integer():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01020000003", "Doctor", "Doctor User")
        first, second, third = seed_search_patients()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/search?q={second.medical_file_number}")

        assert response.status_code == 200
        assert second.formatted_mrn.encode() in response.data
        assert b"Mona Mahmoud" in response.data

        db.drop_all()


def test_search_by_mrn_padded():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01020000004", "Doctor", "Doctor User")
        first, second, third = seed_search_patients()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get(f"/patients/search?q={third.formatted_mrn}")

        assert response.status_code == 200
        assert third.formatted_mrn.encode() in response.data
        assert b"Laila Hassan" in response.data

        db.drop_all()


def test_search_by_phone_returns_duplicate_phone_patients():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01020000005", "Doctor", "Doctor User")
        seed_search_patients()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/patients/search?q=01000000001")

        assert response.status_code == 200
        assert b"Sara Ahmed" in response.data
        assert b"Laila Hassan" in response.data
        assert b"Mona Mahmoud" not in response.data

        db.drop_all()


def test_empty_search_returns_recent_patients():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01020000006", "Doctor", "Doctor User")
        seed_search_patients()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/patients/search?q=")

        assert response.status_code == 200
        assert b"Recent patients" in response.data
        assert b"Sara Ahmed" in response.data
        assert b"Mona Mahmoud" in response.data
        assert b"Laila Hassan" in response.data

        db.drop_all()


def test_patient_index_contains_htmx_search_input():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01020000007", "Doctor", "Doctor User")
        create_patient()

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/patients/")

        assert response.status_code == 200
        assert b'hx-get="/patients/search"' in response.data
        assert b'Patient search' in response.data
        assert b'patient-search-results' in response.data

        db.drop_all()
