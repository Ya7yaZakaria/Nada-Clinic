from app import create_app
from app.extensions import db
from app.models import User
from app.models.drug_dictionary import DrugCategory, DrugSafetyStatus
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
    )
    return app


def create_user(email, role_name):
    user = User(email=email, phone="01077779999", name=role_name)
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


def test_doctor_can_open_drug_settings_page():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-ui@example.com", "Doctor")

        client = app.test_client()
        login(client, "doctor-ui@example.com")

        response = client.get("/drug-settings/")

        assert response.status_code == 200
        assert b"Medication Dictionaries" in response.data

        db.drop_all()


def test_reception_cannot_open_drug_settings_page():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("reception-ui@example.com", "Reception")

        client = app.test_client()
        login(client, "reception-ui@example.com")

        response = client.get("/drug-settings/")

        assert response.status_code == 403

        db.drop_all()


def test_seed_defaults_from_ui_creates_dictionary_items():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-seed@example.com", "Doctor")

        client = app.test_client()
        login(client, "doctor-seed@example.com")

        response = client.post("/drug-settings/seed-defaults", follow_redirects=True)

        assert response.status_code == 200
        assert DrugCategory.query.count() > 0
        assert DrugSafetyStatus.query.filter_by(code="unknown").first()

        db.drop_all()


def test_create_category_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-create@example.com", "Doctor")

        client = app.test_client()
        login(client, "doctor-create@example.com")

        response = client.post(
            "/drug-settings/categories/new",
            data={
                "code": "tocolytic",
                "name_en": "Tocolytic",
                "name_ar": "مانع انقباضات",
                "sort_order": "1",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert DrugCategory.query.filter_by(code="tocolytic").first()

        db.drop_all()


def test_duplicate_category_from_ui_shows_error():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-duplicate@example.com", "Doctor")

        category = DrugCategory(code="antibiotic", name_en="Antibiotic")
        db.session.add(category)
        db.session.commit()

        client = app.test_client()
        login(client, "doctor-duplicate@example.com")

        response = client.post(
            "/drug-settings/categories/new",
            data={
                "code": "antibiotic",
                "name_en": "Duplicate",
                "sort_order": "1",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Dictionary code already exists" in response.data

        db.drop_all()


def test_edit_category_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-edit@example.com", "Doctor")

        category = DrugCategory(code="old_code", name_en="Old")
        db.session.add(category)
        db.session.commit()

        client = app.test_client()
        login(client, "doctor-edit@example.com")

        response = client.post(
            f"/drug-settings/categories/{category.uuid}/edit",
            data={
                "code": "new_code",
                "name_en": "New Name",
                "name_ar": "اسم جديد",
                "sort_order": "2",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert DrugCategory.query.filter_by(code="new_code").first()

        db.drop_all()


def test_deactivate_and_reactivate_category_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-toggle@example.com", "Doctor")

        category = DrugCategory(code="toggle", name_en="Toggle")
        db.session.add(category)
        db.session.commit()

        client = app.test_client()
        login(client, "doctor-toggle@example.com")

        response = client.post(
            f"/drug-settings/categories/{category.uuid}/deactivate",
            follow_redirects=True,
        )
        assert response.status_code == 200
        db.session.refresh(category)
        assert category.is_active is False

        response = client.post(
            f"/drug-settings/categories/{category.uuid}/reactivate",
            follow_redirects=True,
        )
        assert response.status_code == 200
        db.session.refresh(category)
        assert category.is_active is True

        db.drop_all()


def test_create_safety_status_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-safety@example.com", "Doctor")

        client = app.test_client()
        login(client, "doctor-safety@example.com")

        response = client.post(
            "/drug-settings/safety-statuses/new",
            data={
                "code": "monitor",
                "name_en": "Monitor",
                "name_ar": "متابعة",
                "sort_order": "5",
                "severity_order": "2",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert DrugSafetyStatus.query.filter_by(code="monitor").first()

        db.drop_all()
