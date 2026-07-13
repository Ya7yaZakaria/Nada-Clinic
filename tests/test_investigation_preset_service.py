from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.investigation import InvestigationOrderItem, InvestigationResult, InvestigationTest
from app.models.investigation_preset import InvestigationPresetItem
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


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01066440000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Investigation preset visit",
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


def test_investigation_preset_permission_is_seeded_for_doctor_not_reception():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-investigation-preset-rbac@example.com", "01066440001", "Doctor")
        reception = create_user("reception-investigation-preset-rbac@example.com", "01066440002", "Reception")

        assert RBACService.user_has_permission(doctor, "investigation_presets.manage")
        assert not RBACService.user_has_permission(reception, "investigation_presets.manage")

        db.drop_all()


def test_create_update_deactivate_reactivate_preset():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-investigation-preset@example.com", "01066440003", "Doctor")

        preset = InvestigationPresetService.create_preset(
            name="Infertility Workup",
            description="Baseline",
            actor_user=doctor,
        )

        assert preset.name == "Infertility Workup"
        assert preset.description == "Baseline"
        assert preset.created_by_user == doctor

        InvestigationPresetService.update_preset(
            preset,
            name="Basic Infertility Workup",
            description="Updated",
            actor_user=doctor,
        )

        assert preset.name == "Basic Infertility Workup"
        assert preset.description == "Updated"
        assert preset.updated_by_user == doctor

        InvestigationPresetService.deactivate_preset(preset, actor_user=doctor)
        assert not preset.is_active

        InvestigationPresetService.reactivate_preset(preset, actor_user=doctor)
        assert preset.is_active

        db.drop_all()


def test_duplicate_preset_name_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        InvestigationPresetService.create_preset(name="PCOS Workup")

        try:
            InvestigationPresetService.create_preset(name="PCOS Workup")
        except ValueError as exc:
            assert "already exists" in str(exc)
        else:
            raise AssertionError("Duplicate preset name should fail")

        db.drop_all()


def test_add_and_remove_preset_item():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        preset = InvestigationPresetService.create_preset(name="Hormonal Profile")
        test = create_test(code="tsh", name="TSH")

        item = InvestigationPresetService.add_item(
            preset=preset,
            test=test,
            notes="Baseline thyroid",
        )

        assert item.preset == preset
        assert item.test == test
        assert item.notes == "Baseline thyroid"
        assert item.sort_order == 1
        assert preset.items.count() == 1

        InvestigationPresetService.remove_item(item)

        assert InvestigationPresetItem.query.count() == 0

        db.drop_all()


def test_duplicate_test_in_same_preset_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        preset = InvestigationPresetService.create_preset(name="RPL Workup")
        test = create_test(code="tsh_dup", name="TSH")

        InvestigationPresetService.add_item(preset=preset, test=test)

        try:
            InvestigationPresetService.add_item(preset=preset, test=test)
        except ValueError as exc:
            assert "already exists" in str(exc)
        else:
            raise AssertionError("Duplicate test in preset should fail")

        db.drop_all()


def test_inactive_test_cannot_be_added_to_preset():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        preset = InvestigationPresetService.create_preset(name="Pre-op Labs")
        test = create_test(code="cbc", name="CBC")
        InvestigationDictionaryService.deactivate_test(test)

        try:
            InvestigationPresetService.add_item(preset=preset, test=test)
        except ValueError as exc:
            assert "Inactive investigation test" in str(exc)
        else:
            raise AssertionError("Inactive test should fail")

        db.drop_all()


def test_list_items_sorts_by_sort_order():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        preset = InvestigationPresetService.create_preset(name="Sorted Workup")
        first = create_test(code="first_test", name="First")
        second = create_test(code="second_test", name="Second")

        item_2 = InvestigationPresetService.add_item(preset=preset, test=second, sort_order=2)
        item_1 = InvestigationPresetService.add_item(preset=preset, test=first, sort_order=1)

        items = InvestigationPresetService.list_items(preset)

        assert items == [item_1, item_2]

        db.drop_all()


def test_apply_preset_to_order_creates_order_items():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient()
        visit = create_visit(patient)
        amh = create_test(code="apply_amh", name="AMH")
        tsh = create_test(code="apply_tsh", name="TSH")

        preset = InvestigationPresetService.create_preset(name="Infertility Apply Workup")
        InvestigationPresetService.add_item(preset=preset, test=amh, notes="AMH note")
        InvestigationPresetService.add_item(preset=preset, test=tsh, notes="TSH note")

        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)

        created_items = InvestigationPresetService.apply_to_order(
            preset=preset,
            order=order,
        )

        assert len(created_items) == 2
        assert InvestigationOrderItem.query.filter_by(order_id=order.id).count() == 2
        assert created_items[0].status == InvestigationOrderItem.STATUS_PENDING_RESULT
        assert created_items[0].item_notes == "AMH note"

        db.drop_all()


def test_apply_preset_skips_existing_order_tests_and_prevents_all_duplicate_apply():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01066440109")
        visit = create_visit(patient)
        amh = create_test(code="skip_amh", name="AMH")
        tsh = create_test(code="skip_tsh", name="TSH")

        preset = InvestigationPresetService.create_preset(name="Skip Existing Workup")
        InvestigationPresetService.add_item(preset=preset, test=amh)
        InvestigationPresetService.add_item(preset=preset, test=tsh)

        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        InvestigationService.add_order_item(order=order, test=amh)

        created_items = InvestigationPresetService.apply_to_order(
            preset=preset,
            order=order,
        )

        assert len(created_items) == 1
        assert created_items[0].test == tsh
        assert InvestigationOrderItem.query.filter_by(order_id=order.id).count() == 2

        try:
            InvestigationPresetService.apply_to_order(preset=preset, order=order)
        except ValueError as exc:
            assert "already exist" in str(exc)
        else:
            raise AssertionError("Applying all duplicates should fail")

        db.drop_all()


def test_apply_inactive_or_empty_preset_fails():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01066440110")
        visit = create_visit(patient)

        inactive = InvestigationPresetService.create_preset(name="Inactive Workup")
        empty = InvestigationPresetService.create_preset(name="Empty Workup")

        InvestigationPresetService.deactivate_preset(inactive)

        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)

        try:
            InvestigationPresetService.apply_to_order(preset=inactive, order=order)
        except ValueError as exc:
            assert "Inactive investigation preset" in str(exc)
        else:
            raise AssertionError("Inactive preset should fail")

        try:
            InvestigationPresetService.apply_to_order(preset=empty, order=order)
        except ValueError as exc:
            assert "has no items" in str(exc)
        else:
            raise AssertionError("Empty preset should fail")

        db.drop_all()


def test_apply_preset_to_cancelled_order_fails():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01066440111")
        visit = create_visit(patient)
        test = create_test(code="cancelled_order_test", name="AMH")

        preset = InvestigationPresetService.create_preset(name="Cancelled Order Workup")
        InvestigationPresetService.add_item(preset=preset, test=test)

        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        order.status = "cancelled"
        db.session.commit()

        try:
            InvestigationPresetService.apply_to_order(preset=preset, order=order)
        except ValueError as exc:
            assert "cancelled investigation order" in str(exc)
        else:
            raise AssertionError("Applying to cancelled order should fail")

        db.drop_all()


def test_missing_tests_for_patient_uses_latest_results():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01066440112")
        visit = create_visit(patient)
        amh = create_test(code="missing_preset_amh", name="AMH")
        tsh = create_test(code="missing_preset_tsh", name="TSH")
        prolactin = create_test(code="missing_preset_prl", name="Prolactin")

        preset = InvestigationPresetService.create_preset(name="Missing Workup")
        InvestigationPresetService.add_item(preset=preset, test=amh)
        InvestigationPresetService.add_item(preset=preset, test=tsh)
        InvestigationPresetService.add_item(preset=preset, test=prolactin)

        InvestigationService.enter_historical_result(
            patient=patient,
            test=amh,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="1.2",
            abnormal_flag=InvestigationResult.FLAG_NORMAL,
        )

        missing = InvestigationPresetService.missing_tests_for_patient(
            preset=preset,
            patient=patient,
        )

        assert amh not in missing
        assert tsh in missing
        assert prolactin in missing

        db.drop_all()
