
from app import create_app
from app.extensions import db
from app.models import User
from app.services.rbac_service import RBACService


ALLOWED_EMAIL = "ya7ya.zakaria@gmail.com"
PASSWORD = "12345678"


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        DEV_ROLE_PREVIEW_ENABLED=True,
        DEV_ROLE_PREVIEW_EMAILS=ALLOWED_EMAIL,
    )
    return app


def create_user(
    email=ALLOWED_EMAIL,
    phone="01010000001",
):
    user = User(
        email=email,
        phone=phone,
        name="Development Preview User",
    )
    user.set_password(PASSWORD)

    db.session.add(user)
    db.session.commit()

    RBACService.assign_roles(
        user,
        ["Admin", "Doctor"],
    )

    return user


def login(client, email=ALLOWED_EMAIL):
    return client.post(
        "/auth/login",
        data={
            "login_identifier": email,
            "password": PASSWORD,
        },
        follow_redirects=True,
    )


def test_reception_preview_changes_system_permissions():
    app = make_app()

    with app.app_context():
        db.create_all()
        RBACService.seed_roles_permissions()
        create_user()

        with app.test_client() as client:
            login(client)

            response = client.post(
                "/development/role-preview",
                data={"role_name": "Reception"},
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"DEVELOPMENT PREVIEW" in response.data
            assert b"Reception" in response.data

            assert client.get(
                "/clinical-placeholder"
            ).status_code == 403

            assert client.get(
                "/reception-placeholder"
            ).status_code == 200

        db.drop_all()


def test_doctor_preview_blocks_admin_permission():
    app = make_app()

    with app.app_context():
        db.create_all()
        RBACService.seed_roles_permissions()
        create_user()

        with app.test_client() as client:
            login(client)

            client.post(
                "/development/role-preview",
                data={"role_name": "Doctor"},
            )

            assert client.get("/admin/").status_code == 403

            assert client.get(
                "/clinical-placeholder"
            ).status_code == 200

        db.drop_all()


def test_clear_preview_restores_actual_roles():
    app = make_app()

    with app.app_context():
        db.create_all()
        RBACService.seed_roles_permissions()
        create_user()

        with app.test_client() as client:
            login(client)

            client.post(
                "/development/role-preview",
                data={"role_name": "Reception"},
            )

            assert client.get(
                "/clinical-placeholder"
            ).status_code == 403

            response = client.post(
                "/development/role-preview/clear",
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"DEVELOPMENT PREVIEW:" not in response.data

            assert client.get(
                "/clinical-placeholder"
            ).status_code == 200

        db.drop_all()


def test_logout_clears_preview_session():
    app = make_app()

    with app.app_context():
        db.create_all()
        RBACService.seed_roles_permissions()
        create_user()

        with app.test_client() as client:
            login(client)

            client.post(
                "/development/role-preview",
                data={"role_name": "Reception"},
            )

            with client.session_transaction() as session:
                assert (
                    session.get(
                        "development_role_preview"
                    )
                    == "Reception"
                )

            client.post("/auth/logout")

            with client.session_transaction() as session:
                assert (
                    "development_role_preview"
                    not in session
                )

        db.drop_all()


def test_non_allowlisted_user_cannot_preview():
    app = make_app()

    with app.app_context():
        db.create_all()
        RBACService.seed_roles_permissions()

        create_user(
            email="other@example.com",
            phone="01010000002",
        )

        with app.test_client() as client:
            login(
                client,
                email="other@example.com",
            )

            response = client.post(
                "/development/role-preview",
                data={"role_name": "Reception"},
            )

            assert response.status_code == 404

        db.drop_all()


def test_invalid_preview_role_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        RBACService.seed_roles_permissions()
        create_user()

        with app.test_client() as client:
            login(client)

            response = client.post(
                "/development/role-preview",
                data={"role_name": "Unknown"},
            )

            assert response.status_code == 400

        db.drop_all()


def test_preview_disabled_keeps_actual_permissions():
    app = make_app()
    app.config["DEV_ROLE_PREVIEW_ENABLED"] = False

    with app.app_context():
        db.create_all()
        RBACService.seed_roles_permissions()
        create_user()

        with app.test_client() as client:
            login(client)

            response = client.post(
                "/development/role-preview",
                data={"role_name": "Reception"},
            )

            assert response.status_code == 404

            assert client.get(
                "/clinical-placeholder"
            ).status_code == 200

        db.drop_all()
