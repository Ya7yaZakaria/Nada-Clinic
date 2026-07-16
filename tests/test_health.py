from app import create_app
from app.extensions import db
from app.models import User
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_test_user():
    user = User(
        email="doctor@example.com",
        phone="01000000000",
        name="Test Doctor",
    )
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, "Doctor")

    return user


def test_health_endpoint_returns_ok():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.get("/health")

        assert response.status_code == 200
        assert response.get_json()["status"] == "ok"

        db.drop_all()


def test_index_redirects_anonymous_user_to_login():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.get("/")

        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]

        db.drop_all()


def test_index_page_renders_for_logged_in_user():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_test_user()

        with app.test_client() as client:
            client.post(
                "/auth/login",
                data={
                    "login_identifier": "doctor@example.com",
                    "password": "12345678",
                },
            )
            response = client.get("/")

        assert response.status_code == 200
        assert b"Nada Clinic System" in response.data

        db.drop_all()


def test_ui_shell_contains_foundation_navigation_for_logged_in_user():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_test_user()

        with app.test_client() as client:
            client.post(
                "/auth/login",
                data={
                    "login_identifier": "doctor@example.com",
                    "password": "12345678",
                },
            )
            response = client.get("/")

        assert response.status_code == 200
        assert b"Today Clinic" in response.data
        assert b"Patients" in response.data
        assert b"Visits" in response.data
        assert b"Stage 1" not in response.data
        assert b"Appointments" in response.data
        assert b"Investigations" in response.data

        db.drop_all()
