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


def login_without_follow(client, email):
    return client.post(
        "/auth/login",
        data={"login_identifier": email, "password": "12345678"},
        follow_redirects=False,
    )


def setup_admin(email="admin-workflow-stage-12@example.com", phone="01099300001"):
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user(email, phone, "Admin", "Admin User")
        yield app
        db.drop_all()


def test_default_workflow_landing_is_dashboard():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        preferences = SettingsService.get_workflow_preferences()

        assert preferences["default_landing_page"] == "dashboard"
        assert preferences["default_landing_label"] == "Dashboard"
        assert SettingsService.get_default_landing_endpoint_for_user() == "main.index"

        db.drop_all()


def test_existing_auth_tests_keep_dashboard_default():
    for app in setup_admin():
        client = app.test_client()

        response = client.post(
            "/auth/login",
            data={"login_identifier": "admin-workflow-stage-12@example.com", "password": "12345678"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Admin User" in response.data
        assert b"Clinic Dashboard" in response.data
        assert b'id="dashboard-live-clock"' in response.data


def test_login_respects_today_clinic_default_landing():
    for app in setup_admin("admin-workflow-today-stage-12@example.com", "01099300002"):
        SettingsService.set("workflow.default_landing_page", "today_clinic")

        client = app.test_client()
        response = login_without_follow(client, "admin-workflow-today-stage-12@example.com")

        assert response.status_code == 302
        assert response.headers["Location"].endswith("/clinic/today")


def test_login_respects_patients_default_landing():
    for app in setup_admin("admin-workflow-patients-stage-12@example.com", "01099300003"):
        SettingsService.set("workflow.default_landing_page", "patients")

        client = app.test_client()
        response = login_without_follow(client, "admin-workflow-patients-stage-12@example.com")

        assert response.status_code == 302
        assert response.headers["Location"].endswith("/patients/")


def test_invalid_landing_key_falls_back_to_dashboard():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        target = SettingsService.get_landing_target("bad-key")

        assert target["endpoint"] == "main.index"
        assert target["label"] == "Dashboard"

        db.drop_all()


def test_settings_dashboard_shows_workflow_defaults_card():
    for app in setup_admin("admin-workflow-card-stage-12@example.com", "01099300004"):
        client = app.test_client()
        client.post(
            "/auth/login",
            data={"login_identifier": "admin-workflow-card-stage-12@example.com", "password": "12345678"},
            follow_redirects=True,
        )

        response = client.get("/settings/")

        assert response.status_code == 200
        assert b"Workflow Defaults" in response.data
        assert b"Open Workflow Settings" in response.data
        assert b"Dashboard" in response.data
