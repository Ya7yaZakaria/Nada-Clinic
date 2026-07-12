from app import create_app
from app.extensions import db
from app.models import User
from app.models.drug_dictionary import DrugCategory
from app.services.drug_dictionary_service import DrugDictionaryService
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_user(email, role_name):
    user = User(email=email, phone="01055559999", name=role_name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)

    return user


def test_create_category_requires_code():
    app = make_app()

    with app.app_context():
        db.create_all()

        try:
            DrugDictionaryService.create_category(code="", name_en="Antibiotic")
            assert False
        except ValueError as exc:
            assert "Code is required" in str(exc)

        db.drop_all()


def test_create_category_requires_english_name():
    app = make_app()

    with app.app_context():
        db.create_all()

        try:
            DrugDictionaryService.create_category(code="antibiotic", name_en="")
            assert False
        except ValueError as exc:
            assert "English name is required" in str(exc)

        db.drop_all()


def test_duplicate_code_rejected_per_dictionary():
    app = make_app()

    with app.app_context():
        db.create_all()

        DrugDictionaryService.create_category(code="antibiotic", name_en="Antibiotic")

        try:
            DrugDictionaryService.create_category(code="antibiotic", name_en="Duplicate")
            assert False
        except ValueError as exc:
            assert "Dictionary code already exists" in str(exc)

        db.drop_all()


def test_update_category_changes_values():
    app = make_app()

    with app.app_context():
        db.create_all()

        category = DrugDictionaryService.create_category(code="old_code", name_en="Old")
        DrugDictionaryService.update_category(
            category,
            code="new_code",
            name_en="New Name",
            name_ar="اسم جديد",
            sort_order=5,
        )

        assert category.code == "new_code"
        assert category.name_en == "New Name"
        assert category.name_ar == "اسم جديد"
        assert category.sort_order == 5

        db.drop_all()


def test_create_form_route_and_safety_status():
    app = make_app()

    with app.app_context():
        db.create_all()

        form = DrugDictionaryService.create_form(code="tablet", name_en="Tablet")
        route = DrugDictionaryService.create_route(code="oral", name_en="Oral")
        safety = DrugDictionaryService.create_safety_status(
            code="caution",
            name_en="Caution",
            severity_order=2,
        )

        assert form.code == "tablet"
        assert route.code == "oral"
        assert safety.code == "caution"
        assert safety.severity_order == 2

        db.drop_all()


def test_doctor_has_drug_settings_permission():
    app = make_app()

    with app.app_context():
        db.create_all()

        doctor = create_user("doctor@example.com", "Doctor")

        assert RBACService.user_has_permission(doctor, "drug_settings.manage")

        db.drop_all()


def test_admin_has_drug_settings_permission():
    app = make_app()

    with app.app_context():
        db.create_all()

        admin = create_user("admin@example.com", "Admin")

        assert RBACService.user_has_permission(admin, "drug_settings.manage")

        db.drop_all()


def test_reception_is_blocked_from_drug_settings_permission():
    app = make_app()

    with app.app_context():
        db.create_all()

        reception = create_user("reception@example.com", "Reception")

        assert not RBACService.user_has_permission(reception, "drug_settings.manage")

        db.drop_all()


def test_dictionary_tables_exist_without_drug_model():
    app = make_app()

    with app.app_context():
        db.create_all()

        tables = set(db.metadata.tables.keys())

        assert "drug_categories" in tables
        assert "drug_forms" in tables
        assert "drug_routes" in tables
        assert "drug_safety_statuses" in tables
        assert "drugs" not in tables

        db.drop_all()
