from app import create_app
from app.extensions import db
from app.models import User
from app.services.auth_service import AuthService
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_test_user(email="doctor@example.com", phone="01000000000", password="12345678"):
    user = User(email=email, phone=phone, name="Test Doctor")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, "Doctor")

    return user


def test_login_page_renders():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.get("/auth/login")

        assert response.status_code == 200
        assert b"Email or phone" in response.data

        db.drop_all()


def test_dashboard_requires_login():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.get("/")

        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]

        db.drop_all()


def test_invalid_login_fails():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.post(
                "/auth/login",
                data={
                    "login_identifier": "missing@example.com",
                    "password": "wrongpassword",
                },
                follow_redirects=True,
            )

        assert response.status_code == 401
        assert b"Invalid login details" in response.data

        db.drop_all()


def test_valid_email_login_succeeds():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_test_user(email="doctor@example.com", phone="01000000000")

        with app.test_client() as client:
            response = client.post(
                "/auth/login",
                data={
                    "login_identifier": "doctor@example.com",
                    "password": "12345678",
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert b"Welcome, Test Doctor" in response.data

        db.drop_all()


def test_valid_phone_login_succeeds():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_test_user(email="doctor@example.com", phone="01000000000")

        with app.test_client() as client:
            response = client.post(
                "/auth/login",
                data={
                    "login_identifier": "01000000000",
                    "password": "12345678",
                },
                follow_redirects=True,
            )

        assert response.status_code == 200
        assert b"Welcome, Test Doctor" in response.data

        db.drop_all()


def test_logout_works():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_test_user(email="doctor@example.com", phone="01000000000")

        with app.test_client() as client:
            client.post(
                "/auth/login",
                data={
                    "login_identifier": "doctor@example.com",
                    "password": "12345678",
                },
            )

            response = client.post("/auth/logout", follow_redirects=True)

        assert response.status_code == 200
        assert b"Login to Clinic OS" in response.data

        db.drop_all()


def test_password_is_hashed():
    app = make_app()

    with app.app_context():
        db.create_all()

        user = AuthService.create_user(
            email="admin@example.com",
            name="Admin",
            password="12345678",
        )

        assert user.password_hash != "12345678"
        assert user.check_password("12345678")

        db.drop_all()


def test_seed_admin_command_creates_admin_seed(monkeypatch):
    app = make_app()

    monkeypatch.setenv("ADMIN_EMAIL", "seed@example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "12345678")
    monkeypatch.setenv("ADMIN_NAME", "Seed Admin")

    with app.app_context():
        db.create_all()

        runner = app.test_cli_runner()
        result = runner.invoke(args=["seed-admin"])

        user = User.query.filter_by(email="seed@example.com").first()

        assert result.exit_code == 0
        assert user is not None
        assert user.is_admin_seed is True
        assert user.password_hash != "12345678"

        db.drop_all()


def test_health_route_remains_public():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.get("/health")

        assert response.status_code == 200
        assert response.get_json()["status"] == "ok"

        db.drop_all()
