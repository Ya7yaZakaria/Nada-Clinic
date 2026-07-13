from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.investigation import InvestigationOrderItem, InvestigationTest
from app.models.investigation_preset import InvestigationPreset
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_preset_service import InvestigationPresetService
from app.services.investigation_service import InvestigationService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


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


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01066550000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Investigation preset UI visit",
    )


def create_test(code="amh", name="AMH"):
    category = InvestigationDictionaryService.create_category(
        code=f"{code}_category",
        name_en=f"{name} Category",
    )
    return InvestigationDictionaryService.create_test(
        code=code,
        name_en=name,
        category=category,
        default_unit="mIU/L",
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def test_doctor_can_open_investigation_presets_index():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-investigation-presets-index@example.com", "01066550001", "Doctor")

        client = app.test_client()
        login(client, "doctor-investigation-presets-index@example.com")

        response = client.get("/investigation-presets/")

        assert response.status_code == 200
        assert b"Investigation Presets" in response.data
        assert b"New preset" in response.data

        db.drop_all()


def test_doctor_can_create_investigation_preset_from_ui():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-create-investigation-preset-ui@example.com", "01066550002", "Doctor")

        client = app.test_client()
        login(client, "doctor-create-investigation-preset-ui@example.com")

        response = client.post(
            "/investigation-presets/new",
            data={
                "name": "Infertility Workup",
                "description": "Baseline infertility labs",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        preset = InvestigationPreset.query.filter_by(name="Infertility Workup").first()

        assert response.status_code == 200
        assert b"Investigation preset created" in response.data
        assert preset is not None
        assert preset.description == "Baseline infertility labs"

        db.drop_all()


def test_doctor_can_add_and_remove_test_from_investigation_preset():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-edit-investigation-preset-ui@example.com", "01066550003", "Doctor")
        test = create_test(code="ui_tsh", name="TSH")
        preset = InvestigationPresetService.create_preset(name="Hormonal Profile")

        client = app.test_client()
        login(client, "doctor-edit-investigation-preset-ui@example.com")

        add_response = client.post(
            f"/investigation-presets/{preset.uuid}/items",
            data={
                "test_id": str(test.id),
                "notes": "Baseline thyroid",
            },
            follow_redirects=True,
        )

        assert add_response.status_code == 200
        assert b"Investigation test added to preset" in add_response.data
        assert b"TSH" in add_response.data
        assert preset.items.count() == 1

        item = preset.items.first()

        remove_response = client.post(
            f"/investigation-presets/items/{item.uuid}/remove",
            follow_redirects=True,
        )

        assert remove_response.status_code == 200
        assert b"Investigation preset item removed" in remove_response.data
        assert preset.items.count() == 0

        db.drop_all()


def test_doctor_can_apply_investigation_preset_to_order_from_order_detail():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-apply-investigation-preset-ui@example.com", "01066550004", "Doctor")

        patient = create_patient()
        visit = create_visit(patient)
        amh = create_test(code="apply_ui_amh", name="AMH")
        tsh = create_test(code="apply_ui_tsh", name="TSH")

        preset = InvestigationPresetService.create_preset(name="Apply UI Workup")
        InvestigationPresetService.add_item(preset=preset, test=amh)
        InvestigationPresetService.add_item(preset=preset, test=tsh)

        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)

        client = app.test_client()
        login(client, "doctor-apply-investigation-preset-ui@example.com")

        response = client.post(
            f"/investigations/orders/{order.uuid}/apply-preset",
            data={
                "preset_id": str(preset.id),
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Investigation preset applied" in response.data
        assert b"AMH" in response.data
        assert b"TSH" in response.data
        assert InvestigationOrderItem.query.filter_by(order_id=order.id).count() == 2

        db.drop_all()


def test_order_detail_shows_apply_preset_block_for_doctor():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-order-detail-preset-block@example.com", "01066550005", "Doctor")

        patient = create_patient(phone_primary="01066550105")
        visit = create_visit(patient)
        preset = InvestigationPresetService.create_preset(name="Visible Preset")
        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)

        client = app.test_client()
        login(client, "doctor-order-detail-preset-block@example.com")

        response = client.get(f"/investigations/orders/{order.uuid}")

        assert response.status_code == 200
        assert b"Apply investigation preset" in response.data
        assert b"Visible Preset" in response.data

        db.drop_all()


def test_reception_cannot_manage_investigation_presets():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-investigation-presets-ui@example.com", "01066550006", "Reception")

        client = app.test_client()
        login(client, "reception-investigation-presets-ui@example.com")

        response = client.get("/investigation-presets/")

        assert response.status_code == 403

        db.drop_all()


def test_investigation_presets_sidebar_link_exists_for_doctor():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-investigation-preset-sidebar@example.com", "01066550007", "Doctor")

        client = app.test_client()
        login(client, "doctor-investigation-preset-sidebar@example.com")

        response = client.get("/")

        assert response.status_code == 200
        assert b"/investigation-presets/" in response.data
        assert b"Investigation Presets" in response.data

        db.drop_all()
