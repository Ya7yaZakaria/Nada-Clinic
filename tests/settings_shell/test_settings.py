from tests.factories import create_user
from tests.factories import login_follow_redirects as login
from tests.factories import make_app_server as make_app

from app import create_app
from app.extensions import db
from app.models import Setting, User
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


def test_default_settings_can_be_seeded():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        assert Setting.query.filter_by(key="clinic.name").first() is not None
        assert Setting.query.filter_by(key="system.app_name").first() is not None
        assert Setting.query.count() >= 28

        db.drop_all()


def test_admin_can_view_settings():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("admin@example.com", "01010000001", "Admin", "Admin User")

        with app.test_client() as client:
            login(client, "admin@example.com")
            response = client.get("/admin/settings")

        assert response.status_code == 200
        assert b"Settings Foundation" in response.data
        assert b"clinic.name" in response.data

        db.drop_all()


def test_non_admin_doctor_cannot_view_settings():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor@example.com", "01010000002", "Doctor", "Doctor User")

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/admin/settings")

        assert response.status_code == 403
        assert b"Access denied" in response.data

        db.drop_all()


def test_setting_can_be_updated_by_admin():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("admin@example.com", "01010000003", "Admin", "Admin User")

        with app.test_client() as client:
            login(client, "admin@example.com")
            response = client.post(
                "/admin/settings",
                data={
                    "setting__clinic__name": "Nada Women Clinic",
                    "setting__system__app_name": "Nada Clinic System",
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert SettingsService.get("clinic.name") == "Nada Women Clinic"

        db.drop_all()


def test_public_settings_can_be_read_safely():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        public_settings = SettingsService.get_public_settings()

        assert "clinic.name" in public_settings
        assert "system.app_name" in public_settings
        assert "security.session_timeout_minutes" not in public_settings

        db.drop_all()
