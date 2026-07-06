from app import create_app
from app.extensions import db
from app.models import Role, User
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_user(email, phone, name="Test User"):
    user = User(email=email, phone=phone, name=name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()
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


def setup_rbac():
    RBACService.seed_roles_permissions()


def test_roles_and_permissions_seed():
    app = make_app()

    with app.app_context():
        db.create_all()
        setup_rbac()

        assert Role.query.filter_by(name="Admin").first() is not None
        assert Role.query.filter_by(name="Doctor").first() is not None
        assert Role.query.filter_by(name="Reception").first() is not None

        admin = Role.query.filter_by(name="Admin").first()
        permission_names = {permission.name for permission in admin.permissions}

        assert "admin.access" in permission_names
        assert "clinical.note.view" in permission_names
        assert "appointments.manage" in permission_names

        db.drop_all()


def test_user_can_have_more_than_one_role():
    app = make_app()

    with app.app_context():
        db.create_all()
        setup_rbac()

        user = create_user("admin-doctor@example.com", "01000000001")
        RBACService.assign_roles(user, ["Admin", "Doctor"])

        role_names = {role.name for role in user.roles}

        assert role_names == {"Admin", "Doctor"}

        db.drop_all()


def test_multi_role_user_gets_combined_permissions():
    app = make_app()

    with app.app_context():
        db.create_all()
        setup_rbac()

        user = create_user("admin-doctor@example.com", "01000000001")
        RBACService.assign_roles(user, ["Admin", "Doctor"])

        assert RBACService.user_has_permission(user, "admin.access")
        assert RBACService.user_has_permission(user, "clinical.note.write")

        db.drop_all()


def test_admin_can_access_admin_placeholder():
    app = make_app()

    with app.app_context():
        db.create_all()
        setup_rbac()

        user = create_user("admin@example.com", "01000000002", "Admin User")
        RBACService.assign_role(user, "Admin")

        with app.test_client() as client:
            login(client, "admin@example.com")
            response = client.get("/admin/")

        assert response.status_code == 200
        assert b"Admin Placeholder" in response.data

        db.drop_all()


def test_doctor_can_access_clinical_placeholder():
    app = make_app()

    with app.app_context():
        db.create_all()
        setup_rbac()

        user = create_user("doctor@example.com", "01000000003", "Doctor User")
        RBACService.assign_role(user, "Doctor")

        with app.test_client() as client:
            login(client, "doctor@example.com")
            response = client.get("/clinical-placeholder")

        assert response.status_code == 200
        assert b"Clinical Notes Placeholder" in response.data

        db.drop_all()


def test_reception_cannot_access_clinical_notes_placeholder():
    app = make_app()

    with app.app_context():
        db.create_all()
        setup_rbac()

        user = create_user("reception@example.com", "01000000004", "Reception User")
        RBACService.assign_role(user, "Reception")

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.get("/clinical-placeholder")

        assert response.status_code == 403
        assert b"Access denied" in response.data

        db.drop_all()


def test_reception_can_access_reception_placeholder():
    app = make_app()

    with app.app_context():
        db.create_all()
        setup_rbac()

        user = create_user("reception@example.com", "01000000004", "Reception User")
        RBACService.assign_role(user, "Reception")

        with app.test_client() as client:
            login(client, "reception@example.com")
            response = client.get("/reception-placeholder")

        assert response.status_code == 200
        assert b"Reception Placeholder" in response.data

        db.drop_all()


def test_user_without_dashboard_permission_gets_403_after_login():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user("norole@example.com", "01000000005", "No Role User")

        with app.test_client() as client:
            login(client, "norole@example.com")
            response = client.get("/")

        assert response.status_code == 403
        assert b"Access denied" in response.data

        db.drop_all()
