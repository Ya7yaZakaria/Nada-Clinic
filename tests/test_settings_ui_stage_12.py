from app import create_app
from app.extensions import db
from app.models import Setting, User
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


def setup_context(role="Admin", email="admin-settings-stage-12@example.com", phone="01099000001"):
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        user = create_user(email, phone, role, role)
        yield app, user
        db.drop_all()


def test_admin_can_open_stage_12_settings_dashboard():
    for app, admin in setup_context():
        client = app.test_client()
        login(client, "admin-settings-stage-12@example.com")

        response = client.get("/settings/")

        assert response.status_code == 200
        assert b"Settings & Personalization" in response.data
        assert b"Appearance" in response.data
        assert b"Localization" in response.data
        assert b"Clinic" in response.data


def test_admin_can_open_settings_group():
    for app, admin in setup_context(email="admin-settings-group@example.com", phone="01099000002"):
        client = app.test_client()
        login(client, "admin-settings-group@example.com")

        response = client.get("/settings/appearance")

        assert response.status_code == 200
        assert b"Theme" in response.data
        assert b"appearance.theme" in response.data


def test_admin_can_edit_theme_and_language_settings():
    for app, admin in setup_context(email="admin-settings-edit@example.com", phone="01099000003"):
        client = app.test_client()
        login(client, "admin-settings-edit@example.com")

        theme_response = client.post(
            "/settings/edit/appearance.theme",
            data={"value": "dark"},
            follow_redirects=True,
        )
        assert theme_response.status_code == 200
        assert SettingsService.get("appearance.theme") == "dark"

        language_response = client.post(
            "/settings/edit/localization.language",
            data={"value": "ar"},
            follow_redirects=True,
        )
        assert language_response.status_code == 200
        assert SettingsService.get("localization.language") == "ar"


def test_invalid_choice_is_rejected():
    for app, admin in setup_context(email="admin-settings-invalid@example.com", phone="01099000004"):
        client = app.test_client()
        login(client, "admin-settings-invalid@example.com")

        response = client.post(
            "/settings/edit/appearance.theme",
            data={"value": "neon"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert SettingsService.get("appearance.theme") == "light"
        assert b"Invalid value" in response.data


def test_seed_defaults_route_keeps_settings_available():
    for app, admin in setup_context(email="admin-settings-seed@example.com", phone="01099000005"):
        Setting.query.filter_by(key="appearance.font_size").delete()
        db.session.commit()
        assert Setting.query.filter_by(key="appearance.font_size").first() is None

        client = app.test_client()
        login(client, "admin-settings-seed@example.com")

        response = client.post("/settings/seed-defaults", follow_redirects=True)

        assert response.status_code == 200
        assert Setting.query.filter_by(key="appearance.font_size").first() is not None


def test_reception_is_blocked_from_settings_dashboard():
    for app, reception in setup_context("Reception", "reception-settings-stage-12@example.com", "01099000006"):
        client = app.test_client()
        login(client, "reception-settings-stage-12@example.com")

        response = client.get("/settings/", follow_redirects=True)

        assert response.status_code == 403


def test_doctor_remains_blocked_from_legacy_admin_settings():
    for app, doctor in setup_context("Doctor", "doctor-settings-stage-12@example.com", "01099000007"):
        client = app.test_client()
        login(client, "doctor-settings-stage-12@example.com")

        response = client.get("/admin/settings", follow_redirects=True)

        assert response.status_code == 403
