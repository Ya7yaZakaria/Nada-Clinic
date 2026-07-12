from app import create_app
from app.extensions import db
from app.models import User
from app.models.drug import Drug
from app.models.drug_dictionary import DrugForm, DrugRoute
from app.models.prescription_preset import PrescriptionPresetItem
from app.services.prescription_preset_service import PrescriptionPresetService
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
    )
    return app


def create_user(email, role_name, phone):
    user = User(email=email, phone=phone, name=role_name)
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


def create_drug(active=True, trade_name="Tavanic", code_suffix=""):
    form = DrugForm(code=f"tablet{code_suffix}", name_en=f"Tablet{code_suffix}")
    route = DrugRoute(code=f"oral{code_suffix}", name_en=f"Oral{code_suffix}")
    db.session.add_all([form, route])
    db.session.commit()

    drug = Drug(
        generic_name="Levofloxacin",
        trade_name=trade_name,
        strength="500 mg",
        form=form,
        route=route,
        is_active=active,
    )
    db.session.add(drug)
    db.session.commit()

    return drug, route


def test_doctor_can_open_prescription_presets_list_page():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-preset-ui@example.com", "Doctor", "01055220001")

        client = app.test_client()
        login(client, "doctor-preset-ui@example.com")

        response = client.get("/prescription-presets/")

        assert response.status_code == 200
        assert b"Prescription Presets" in response.data

        db.drop_all()


def test_reception_cannot_open_prescription_presets_list_page():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("reception-preset-ui@example.com", "Reception", "01055220002")

        client = app.test_client()
        login(client, "reception-preset-ui@example.com")

        response = client.get("/prescription-presets/")

        assert response.status_code == 403

        db.drop_all()


def test_create_prescription_preset_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-create-preset-ui@example.com", "Doctor", "01055220003")

        client = app.test_client()
        login(client, "doctor-create-preset-ui@example.com")

        response = client.post(
            "/prescription-presets/new",
            data={
                "name": "Sinusitis",
                "description": "Common sinusitis preset",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Sinusitis" in response.data
        assert PrescriptionPresetService.list_all_presets()[0].name == "Sinusitis"

        db.drop_all()


def test_duplicate_prescription_preset_from_ui_shows_error():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-duplicate-preset-ui@example.com", "Doctor", "01055220004")
        PrescriptionPresetService.create_preset(name="UTI")

        client = app.test_client()
        login(client, "doctor-duplicate-preset-ui@example.com")

        response = client.post(
            "/prescription-presets/new",
            data={
                "name": "UTI",
                "description": "Duplicate",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"already exists" in response.data

        db.drop_all()


def test_edit_prescription_preset_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-edit-preset-ui@example.com", "Doctor", "01055220005")
        preset = PrescriptionPresetService.create_preset(
            name="Old Preset",
            description="Old description",
        )

        client = app.test_client()
        login(client, "doctor-edit-preset-ui@example.com")

        response = client.post(
            f"/prescription-presets/{preset.uuid}/edit",
            data={
                "name": "New Preset",
                "description": "New description",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        db.session.refresh(preset)

        assert response.status_code == 200
        assert preset.name == "New Preset"
        assert preset.description == "New description"

        db.drop_all()


def test_deactivate_and_reactivate_prescription_preset_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-toggle-preset-ui@example.com", "Doctor", "01055220006")
        preset = PrescriptionPresetService.create_preset(name="Toggle Preset")

        client = app.test_client()
        login(client, "doctor-toggle-preset-ui@example.com")

        response = client.post(
            f"/prescription-presets/{preset.uuid}/deactivate",
            follow_redirects=True,
        )
        db.session.refresh(preset)

        assert response.status_code == 200
        assert preset.is_active is False

        response = client.post(
            f"/prescription-presets/{preset.uuid}/reactivate",
            follow_redirects=True,
        )
        db.session.refresh(preset)

        assert response.status_code == 200
        assert preset.is_active is True

        db.drop_all()


def test_add_prescription_preset_item_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-add-preset-item-ui@example.com", "Doctor", "01055220007")
        drug, route = create_drug()
        preset = PrescriptionPresetService.create_preset(name="Sinusitis")

        client = app.test_client()
        login(client, "doctor-add-preset-item-ui@example.com")

        response = client.post(
            f"/prescription-presets/{preset.uuid}/items",
            data={
                "drug_id": str(drug.id),
                "route_id": str(route.id),
                "dose": "1 tablet",
                "frequency": "Every 24 hours",
                "duration": "5 days",
                "instructions_ar": "قرص مرة يوميًا لمدة ٥ أيام",
            },
            follow_redirects=True,
        )

        items = PrescriptionPresetService.list_items(preset)

        assert response.status_code == 200
        assert b"Tavanic" in response.data
        assert len(items) == 1
        assert items[0].drug == drug

        db.drop_all()


def test_edit_prescription_preset_item_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-edit-preset-item-ui@example.com", "Doctor", "01055220008")
        drug, route = create_drug()
        preset = PrescriptionPresetService.create_preset(name="Sinusitis")
        item = PrescriptionPresetService.add_item(
            preset=preset,
            drug=drug,
            dose="1 tablet",
            frequency="Every 24 hours",
            duration="5 days",
            instructions_ar="تعليمات قديمة",
            route=route,
        )

        client = app.test_client()
        login(client, "doctor-edit-preset-item-ui@example.com")

        response = client.post(
            f"/prescription-presets/items/{item.uuid}/edit",
            data={
                "drug_id": str(drug.id),
                "route_id": str(route.id),
                "dose": "2 tablets",
                "frequency": "Every 12 hours",
                "duration": "7 days",
                "instructions_ar": "تعليمات جديدة",
            },
            follow_redirects=True,
        )

        db.session.refresh(item)

        assert response.status_code == 200
        assert item.dose == "2 tablets"
        assert item.frequency == "Every 12 hours"
        assert item.duration == "7 days"
        assert item.instructions_ar == "تعليمات جديدة"

        db.drop_all()


def test_remove_prescription_preset_item_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user("doctor-remove-preset-item-ui@example.com", "Doctor", "01055220009")
        drug, route = create_drug()
        preset = PrescriptionPresetService.create_preset(name="Sinusitis")
        item = PrescriptionPresetService.add_item(
            preset=preset,
            drug=drug,
            dose="1 tablet",
            frequency="Every 24 hours",
            duration="5 days",
            instructions_ar="تعليمات",
            route=route,
        )
        item_uuid = item.uuid
        item_id = item.id

        client = app.test_client()
        login(client, "doctor-remove-preset-item-ui@example.com")

        response = client.post(
            f"/prescription-presets/items/{item_uuid}/remove",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert db.session.get(PrescriptionPresetItem, item_id) is None

        db.drop_all()
