from tests.factories import make_app_server as make_app, set_test_password

from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import User
from app.services.rbac_service import RBACService


def login_test_user(client):
    user = User(email="doctor@example.com", phone="01000000000", name="Test Doctor")
    set_test_password(user, "12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, "Doctor")

    client.post(
        "/auth/login",
        data={
            "login_identifier": "doctor@example.com",
            "password": "12345678",
        },
    )


def test_base_template_references_pwa_placeholders():
    app = make_app()

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            login_test_user(client)
            response = client.get("/")

        assert response.status_code == 200
        assert b"manifest.json" in response.data
        assert b"service-worker.js" in response.data

        db.drop_all()
