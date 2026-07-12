from app import create_app
from app.extensions import db
from app.models import User
from app.models.drug import Drug
from app.models.drug_dictionary import DrugCategory, DrugForm, DrugRoute, DrugSafetyStatus
from app.services.drug_service import DrugService
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
    )
    return app


def create_user(email, role_name):
    user = User(email=email, phone="01088889999", name=role_name)
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


def create_dictionary_items():
    category = DrugCategory(code="antibiotic", name_en="Antibiotic")
    form = DrugForm(code="tablet", name_en="Tablet")
    injection_form = DrugForm(code="injection", name_en="Injection")
    route = DrugRoute(code="oral", name_en="Oral")
    pregnancy_status = DrugSafetyStatus(code="caution", name_en="Caution", severity_order=2)
    lactation_status = DrugSafetyStatus(code="safe", name_en="Safe", severity_order=1)

    db.session.add_all([category, form, injection_form, route, pregnancy_status, lactation_status])
    db.session.commit()

    return {
        "category": category,
        "form": form,
        "injection_form": injection_form,
        "route": route,
        "pregnancy_status": pregnancy_status,
        "lactation_status": lactation_status,
    }


def test_doctor_can_open_drug_list_page():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-drugs@example.com", "Doctor")

        client = app.test_client()
        login(client, "doctor-drugs@example.com")

        response = client.get("/drugs/")

        assert response.status_code == 200
        assert b"Drug Database" in response.data

        db.drop_all()


def test_reception_cannot_open_drug_list_page():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("reception-drugs@example.com", "Reception")

        client = app.test_client()
        login(client, "reception-drugs@example.com")

        response = client.get("/drugs/")

        assert response.status_code == 403

        db.drop_all()


def test_create_drug_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-create-drug@example.com", "Doctor")
        refs = create_dictionary_items()

        client = app.test_client()
        login(client, "doctor-create-drug@example.com")

        response = client.post(
            "/drugs/new",
            data={
                "trade_name": "Tavanic",
                "generic_name": "Levofloxacin",
                "strength": "500 mg",
                "category_id": str(refs["category"].id),
                "form_id": str(refs["form"].id),
                "route_id": str(refs["route"].id),
                "pregnancy_status_id": str(refs["pregnancy_status"].id),
                "pregnancy_note": "Review before use",
                "lactation_status_id": str(refs["lactation_status"].id),
                "lactation_note": "Doctor note",
                "doctor_notes": "Clinic note",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert Drug.query.filter_by(trade_name="Tavanic").first()

        db.drop_all()


def test_duplicate_drug_from_ui_shows_error():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-duplicate-drug@example.com", "Doctor")
        refs = create_dictionary_items()

        DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            form=refs["form"],
        )

        client = app.test_client()
        login(client, "doctor-duplicate-drug@example.com")

        response = client.post(
            "/drugs/new",
            data={
                "trade_name": "Tavanic",
                "generic_name": "Levofloxacin",
                "strength": "500 mg",
                "form_id": str(refs["form"].id),
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Drug already exists" in response.data

        db.drop_all()


def test_edit_drug_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-edit-drug@example.com", "Doctor")
        refs = create_dictionary_items()

        drug = DrugService.create_drug(
            generic_name="Old Generic",
            trade_name="Old Trade",
            strength="100 mg",
            form=refs["form"],
            category=refs["category"],
            route=refs["route"],
        )

        client = app.test_client()
        login(client, "doctor-edit-drug@example.com")

        response = client.post(
            f"/drugs/{drug.uuid}/edit",
            data={
                "trade_name": "New Trade",
                "generic_name": "New Generic",
                "strength": "200 mg",
                "category_id": "0",
                "form_id": str(refs["injection_form"].id),
                "route_id": "0",
                "pregnancy_status_id": "0",
                "lactation_status_id": "0",
                "doctor_notes": "Updated note",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        db.session.refresh(drug)

        assert response.status_code == 200
        assert drug.trade_name == "New Trade"
        assert drug.generic_name == "New Generic"
        assert drug.strength == "200 mg"
        assert drug.form.code == "injection"
        assert drug.category is None
        assert drug.route is None

        db.drop_all()


def test_deactivate_and_reactivate_drug_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-toggle-drug@example.com", "Doctor")
        refs = create_dictionary_items()

        drug = DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            form=refs["form"],
        )

        client = app.test_client()
        login(client, "doctor-toggle-drug@example.com")

        response = client.post(f"/drugs/{drug.uuid}/deactivate", follow_redirects=True)
        db.session.refresh(drug)

        assert response.status_code == 200
        assert drug.is_active is False

        response = client.post(f"/drugs/{drug.uuid}/reactivate", follow_redirects=True)
        db.session.refresh(drug)

        assert response.status_code == 200
        assert drug.is_active is True

        db.drop_all()


def test_search_drugs_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-search-drug@example.com", "Doctor")
        refs = create_dictionary_items()

        DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            form=refs["form"],
        )
        DrugService.create_drug(
            generic_name="Paracetamol",
            trade_name="Doliprane",
            strength="1000 mg",
            form=refs["form"],
        )

        client = app.test_client()
        login(client, "doctor-search-drug@example.com")

        response = client.get("/drugs/?q=Tavanic")

        assert response.status_code == 200
        assert b"Tavanic" in response.data
        assert b"Doliprane" not in response.data

        db.drop_all()
