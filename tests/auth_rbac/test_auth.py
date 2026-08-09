from app.extensions import db
from app.models import User
from app.services.auth_service import AuthService
from app.services.rbac_service import RBACService
from tests.factories import set_test_password


def create_test_user(email="doctor@example.com", phone="01000000000", password="12345678"):
    user = User(email=email, phone=phone, name="Test Doctor")
    set_test_password(user, password)
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, "Doctor")

    return user


def test_login_page_renders(client):
    response = client.get("/auth/login")

    assert response.status_code == 200
    assert b"Email or phone" in response.data
    assert b"Welcome back" in response.data
    assert b'class="auth-page"' in response.data
    assert b"Stage 1" not in response.data
    assert b"Sprint 1.1" not in response.data
    assert b"Login to Clinic OS" not in response.data
    assert b'class="clinic-sidebar' not in response.data
    assert b'class="clinic-topbar' not in response.data


def test_dashboard_requires_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_invalid_login_fails(client):
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


def test_valid_email_login_succeeds(client):
    create_test_user(email="doctor@example.com", phone="01000000000")

    response = client.post(
        "/auth/login",
        data={
            "login_identifier": "doctor@example.com",
            "password": "12345678",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Test Doctor" in response.data
    assert b"Clinic Dashboard" in response.data
    assert b'id="dashboard-live-clock"' in response.data


def test_valid_phone_login_succeeds(client):
    create_test_user(email="doctor@example.com", phone="01000000000")

    response = client.post(
        "/auth/login",
        data={
            "login_identifier": "01000000000",
            "password": "12345678",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Test Doctor" in response.data
    assert b"Clinic Dashboard" in response.data
    assert b'id="dashboard-live-clock"' in response.data


def test_logout_works(client):
    create_test_user(email="doctor@example.com", phone="01000000000")

    client.post(
        "/auth/login",
        data={
            "login_identifier": "doctor@example.com",
            "password": "12345678",
        },
    )
    response = client.post("/auth/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back" in response.data
    assert b"Sign in to access the clinic workspace" in response.data


def test_password_is_hashed(app):
    user = AuthService.create_user(
        email="admin@example.com",
        name="Admin",
        password="12345678",
    )

    assert user.password_hash != "12345678"
    assert user.check_password("12345678")


def test_seed_admin_command_creates_admin_seed(monkeypatch, app):
    monkeypatch.setenv("ADMIN_EMAIL", "seed@example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "12345678")
    monkeypatch.setenv("ADMIN_NAME", "Seed Admin")

    runner = app.test_cli_runner()
    result = runner.invoke(args=["seed-admin"])

    user = User.query.filter_by(email="seed@example.com").first()

    assert result.exit_code == 0
    assert user is not None
    assert user.is_admin_seed is True
    assert user.password_hash != "12345678"


def test_health_route_remains_public(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_index_page_renders_for_logged_in_user(client):
    create_test_user()
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


def test_ui_shell_contains_foundation_navigation_for_logged_in_user(client):
    create_test_user()
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
