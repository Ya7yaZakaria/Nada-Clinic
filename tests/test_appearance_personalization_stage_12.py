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


def setup_admin(email="admin-appearance-stage-12@example.com", phone="01099100001"):
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user(email, phone, "Admin", "Admin User")
        yield app
        db.drop_all()


def test_default_layout_attributes_are_rendered():
    for app in setup_admin():
        client = app.test_client()
        login(client, "admin-appearance-stage-12@example.com")

        response = client.get("/settings/")

        assert response.status_code == 200
        assert b'lang="en"' in response.data
        assert b'dir="ltr"' in response.data
        assert b'data-bs-theme="light"' in response.data
        assert b'data-theme="light"' in response.data
        assert b'data-accent="teal"' in response.data


def test_dark_theme_setting_controls_bootstrap_theme():
    for app in setup_admin("admin-dark-stage-12@example.com", "01099100002"):
        SettingsService.set("appearance.theme", "dark")

        client = app.test_client()
        login(client, "admin-dark-stage-12@example.com")

        response = client.get("/settings/")

        assert response.status_code == 200
        assert b'data-bs-theme="dark"' in response.data
        assert b'data-theme="dark"' in response.data


def test_auto_theme_keeps_safe_bootstrap_fallback():
    for app in setup_admin("admin-auto-stage-12@example.com", "01099100003"):
        SettingsService.set("appearance.theme", "auto")

        client = app.test_client()
        login(client, "admin-auto-stage-12@example.com")

        response = client.get("/settings/")

        assert response.status_code == 200
        assert b'data-bs-theme="light"' in response.data
        assert b'data-theme="auto"' in response.data


def test_arabic_language_sets_rtl_direction():
    for app in setup_admin("admin-ar-stage-12@example.com", "01099100004"):
        SettingsService.set("localization.language", "ar")

        client = app.test_client()
        login(client, "admin-ar-stage-12@example.com")

        response = client.get("/settings/")

        assert response.status_code == 200
        assert b'lang="ar"' in response.data
        assert b'dir="rtl"' in response.data


def test_accent_font_and_density_attributes_are_rendered():
    for app in setup_admin("admin-density-stage-12@example.com", "01099100005"):
        SettingsService.set("appearance.accent_color", "purple")
        SettingsService.set("appearance.font_size", "large")
        SettingsService.set("appearance.sidebar_density", "compact")
        SettingsService.set("appearance.card_density", "compact")
        SettingsService.set("appearance.table_density", "compact")

        client = app.test_client()
        login(client, "admin-density-stage-12@example.com")

        response = client.get("/settings/")

        assert response.status_code == 200
        assert b'data-accent="purple"' in response.data
        assert b'data-font-size="large"' in response.data
        assert b'data-sidebar-density="compact"' in response.data
        assert b'data-card-density="compact"' in response.data
        assert b'data-table-density="compact"' in response.data


def test_ui_preferences_helper_returns_expected_direction_and_theme():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        SettingsService.set("appearance.theme", "dark")
        SettingsService.set("localization.language", "ar")

        preferences = SettingsService.get_ui_preferences()

        assert preferences["theme"] == "dark"
        assert preferences["bootstrap_theme"] == "dark"
        assert preferences["language"] == "ar"
        assert preferences["direction"] == "rtl"

        db.drop_all()
