from app import create_app
from app.extensions import db
from app.models import User
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost", WTF_CSRF_ENABLED=False)
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
        data={"login_identifier": email, "password": "12345678"},
        follow_redirects=True,
    )


def setup_context(email="admin-clinic-profile-stage-12@example.com", phone="01099200001"):
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user(email, phone, "Admin", "Admin User")
        yield app
        db.drop_all()


def test_clinic_profile_helper_returns_default_profile():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        profile = SettingsService.get_clinic_profile()

        assert profile["name"] == "Nada Clinic System"
        assert profile["short_name"] == "Nada Clinic"
        assert "phone" in profile
        assert "whatsapp" in profile
        assert "address" in profile
        assert "logo_path" in profile
        assert "default_doctor_name" in profile

        db.drop_all()


def test_admin_can_open_clinic_profile_page():
    for app in setup_context():
        client = app.test_client()
        login(client, "admin-clinic-profile-stage-12@example.com")

        response = client.get("/settings/clinic-profile")

        assert response.status_code == 200
        assert b"Clinic Profile Settings" in response.data
        assert b"clinic.name" in response.data
        assert b"clinic.short_name" in response.data
        assert b"clinic.phone" in response.data
        assert b"clinic.whatsapp" in response.data
        assert b"clinic.address" in response.data
        assert b"clinic.logo_path" in response.data
        assert b"clinic.default_doctor_name" in response.data


def test_settings_dashboard_links_to_clinic_profile():
    for app in setup_context("admin-clinic-dashboard-stage-12@example.com", "01099200002"):
        client = app.test_client()
        login(client, "admin-clinic-dashboard-stage-12@example.com")

        response = client.get("/settings/")

        assert response.status_code == 200
        assert b"Clinic Profile" in response.data
        assert b"/settings/clinic-profile" in response.data


def test_clinic_profile_updates_shell_brand_title():
    for app in setup_context("admin-clinic-brand-stage-12@example.com", "01099200003"):
        SettingsService.set("clinic.name", "Nada Women Health Clinic")
        SettingsService.set("clinic.short_name", "Nada Women")

        client = app.test_client()
        login(client, "admin-clinic-brand-stage-12@example.com")

        response = client.get("/settings/clinic-profile")

        assert response.status_code == 200
        assert b"Nada Women Health Clinic" in response.data
        assert b"Nada Women" in response.data


def test_clinic_profile_edit_route_updates_clinic_setting():
    for app in setup_context("admin-clinic-edit-stage-12@example.com", "01099200004"):
        client = app.test_client()
        login(client, "admin-clinic-edit-stage-12@example.com")

        response = client.post(
            "/settings/edit/clinic.phone",
            data={"value": "01000000000"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert SettingsService.get("clinic.phone") == "01000000000"


def test_reception_is_blocked_from_clinic_profile_settings():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user(
            "reception-clinic-profile-stage-12@example.com",
            "01099200005",
            "Reception",
            "Reception User",
        )

        client = app.test_client()
        login(client, "reception-clinic-profile-stage-12@example.com")

        response = client.get("/settings/clinic-profile")

        assert response.status_code == 403

        db.drop_all()
