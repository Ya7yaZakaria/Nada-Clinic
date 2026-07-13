from app import create_app
from app.extensions import db
from app.models import User
from app.models.print_template import PrintTemplate
from app.services.print_template_service import PrintTemplateService
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
    )
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
        data={
            "login_identifier": email,
            "password": "12345678",
        },
        follow_redirects=True,
    )


def test_doctor_can_open_print_templates_index():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-print-templates-index@example.com", "01069030001", "Doctor")

        client = app.test_client()
        login(client, "doctor-print-templates-index@example.com")

        response = client.get("/print/templates/")

        assert response.status_code == 200
        assert b"Print Templates" in response.data
        assert b"Seed defaults" in response.data

        db.drop_all()


def test_reception_cannot_open_print_templates_index():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("reception-print-templates-index@example.com", "01069030002", "Reception")

        client = app.test_client()
        login(client, "reception-print-templates-index@example.com")

        response = client.get("/print/templates/")

        assert response.status_code == 403

        db.drop_all()


def test_doctor_can_seed_default_print_templates_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-print-templates-seed@example.com", "01069030003", "Doctor")

        client = app.test_client()
        login(client, "doctor-print-templates-seed@example.com")

        response = client.post("/print/templates/seed-defaults", follow_redirects=True)

        assert response.status_code == 200
        assert b"Default print templates are ready" in response.data
        assert b"Default Prescription Layout" in response.data
        assert b"Default Investigation Request Layout" in response.data
        assert len(PrintTemplate.query.all()) == 2

        db.drop_all()


def test_doctor_can_create_print_template_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-print-templates-create@example.com", "01069030004", "Doctor")

        client = app.test_client()
        login(client, "doctor-print-templates-create@example.com")

        response = client.post(
            "/print/templates/new",
            data={
                "document_type": PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
                "name": "Nada Small Rx",
                "paper_width_mm": "105",
                "paper_height_mm": "148",
                "is_default": "y",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        template = PrintTemplate.query.filter_by(name="Nada Small Rx").first()

        assert response.status_code == 200
        assert template is not None
        assert template.document_type == PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION
        assert template.is_default is True
        assert b"Print layout" in response.data or b"Paper canvas" in response.data

        db.drop_all()


def test_doctor_can_open_designer_and_save_layout():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-print-templates-designer@example.com", "01069030005", "Doctor")
        template = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST,
            name="Investigation Designer Layout",
        )

        client = app.test_client()
        login(client, "doctor-print-templates-designer@example.com")

        response = client.get(f"/print/templates/{template.uuid}/designer")

        assert response.status_code == 200
        assert b"Paper canvas" in response.data
        assert b"investigation_items" in response.data

        response = client.post(
            f"/print/templates/{template.uuid}/layout",
            data={
                "layout_json": '{"patient_name": {"label": "Patient Name", "x": 30, "y": 40, "visible": true}}',
            },
            follow_redirects=True,
        )

        db.session.refresh(template)

        assert response.status_code == 200
        assert b"Print layout saved" in response.data
        assert template.layout_json["patient_name"]["x"] == 30
        assert template.layout_json["patient_name"]["y"] == 40

        db.drop_all()


def test_designer_rejects_invalid_layout_json():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-print-templates-invalid-json@example.com", "01069030006", "Doctor")
        template = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
            name="Bad Json Layout",
        )

        client = app.test_client()
        login(client, "doctor-print-templates-invalid-json@example.com")

        response = client.post(
            f"/print/templates/{template.uuid}/layout",
            data={
                "layout_json": "{not-json}",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Invalid layout JSON" in response.data

        db.drop_all()


def test_doctor_can_deactivate_and_reactivate_print_template():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-print-templates-toggle@example.com", "01069030007", "Doctor")
        template = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
            name="Toggle Layout",
        )

        client = app.test_client()
        login(client, "doctor-print-templates-toggle@example.com")

        response = client.post(
            f"/print/templates/{template.uuid}/deactivate",
            follow_redirects=True,
        )
        db.session.refresh(template)

        assert response.status_code == 200
        assert template.is_active is False

        response = client.post(
            f"/print/templates/{template.uuid}/reactivate",
            follow_redirects=True,
        )
        db.session.refresh(template)

        assert response.status_code == 200
        assert template.is_active is True

        db.drop_all()


def test_print_templates_sidebar_link_visible_for_doctor():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-print-templates-sidebar@example.com", "01069030008", "Doctor")

        client = app.test_client()
        login(client, "doctor-print-templates-sidebar@example.com")

        response = client.get("/")

        assert response.status_code == 200
        assert b"Print Templates" in response.data
        assert response.data.count(b"Print Templates") == 2

        db.drop_all()
