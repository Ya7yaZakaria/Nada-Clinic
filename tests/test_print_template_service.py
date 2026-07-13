import pytest

from app import create_app
from app.extensions import db
from app.models import User
from app.models.print_template import PrintTemplate
from app.services.print_template_service import PrintTemplateService
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_user(email, phone, role_name, name="Test User"):
    user = User(email=email, phone=phone, name=name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)
    return user


def test_service_creates_default_templates_idempotently():
    app = make_app()

    with app.app_context():
        db.create_all()

        created = PrintTemplateService.ensure_default_templates()
        second_run = PrintTemplateService.ensure_default_templates()

        assert set(created.keys()) == {
            PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
            PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST,
        }
        assert created[PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION].is_default is True
        assert created[PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST].is_default is True
        assert len(PrintTemplate.query.all()) == 2
        assert second_run[PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION].id == created[PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION].id

        db.drop_all()


def test_service_creates_and_updates_template_layout():
    app = make_app()

    with app.app_context():
        db.create_all()

        template = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
            name="Custom Prescription Layout",
            paper_width_mm=100,
            paper_height_mm=140,
            layout_json={"patient_name": {"x": 10, "y": 15}},
        )

        updated = PrintTemplateService.update_template(
            template,
            paper_width_mm=120,
            layout_json={"patient_name": {"x": 20, "y": 25}},
        )

        assert updated.paper_width_mm == 120
        assert updated.paper_height_mm == 140
        assert updated.layout_json["patient_name"]["x"] == 20

        db.drop_all()


def test_service_keeps_only_one_default_per_document_type():
    app = make_app()

    with app.app_context():
        db.create_all()

        first = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST,
            name="First Investigation Layout",
            is_default=True,
        )
        second = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST,
            name="Second Investigation Layout",
            is_default=True,
        )

        db.session.refresh(first)
        db.session.refresh(second)

        assert first.is_default is False
        assert second.is_default is True
        assert PrintTemplateService.get_default_template(
            PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST
        ).id == second.id

        db.drop_all()


def test_service_blocks_duplicate_name_within_same_document_type():
    app = make_app()

    with app.app_context():
        db.create_all()

        PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
            name="Duplicate Layout",
        )

        with pytest.raises(ValueError, match="already exists"):
            PrintTemplateService.create_template(
                document_type=PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
                name="Duplicate Layout",
            )

        db.drop_all()


def test_service_allows_same_name_across_document_types():
    app = make_app()

    with app.app_context():
        db.create_all()

        prescription_template = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
            name="Nada Paper",
        )
        investigation_template = PrintTemplateService.create_template(
            document_type=PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST,
            name="Nada Paper",
        )

        assert prescription_template.id != investigation_template.id

        db.drop_all()


def test_service_blocks_invalid_document_type():
    app = make_app()

    with app.app_context():
        db.create_all()

        with pytest.raises(ValueError, match="Unsupported print document type"):
            PrintTemplateService.create_template(
                document_type="sick_leave",
                name="Invalid Layout",
            )

        db.drop_all()


def test_print_template_permission_seeded_for_doctor_and_admin_not_reception():
    app = make_app()

    with app.app_context():
        db.create_all()

        admin = create_user("admin-print-template@example.com", "01068030001", "Admin")
        doctor = create_user("doctor-print-template@example.com", "01068030002", "Doctor")
        reception = create_user("reception-print-template@example.com", "01068030003", "Reception")

        assert RBACService.user_has_permission(admin, "print_templates.manage")
        assert RBACService.user_has_permission(doctor, "print_templates.manage")
        assert not RBACService.user_has_permission(reception, "print_templates.manage")

        db.drop_all()
