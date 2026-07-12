from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import User
from app.models.drug import Drug
from app.models.drug_dictionary import DrugForm, DrugRoute
from app.models.patient import Patient
from app.models.prescription import PrescriptionItem
from app.services.patient_service import PatientService
from app.services.prescription_preset_service import PrescriptionPresetService
from app.services.prescription_service import PrescriptionService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.models.visit import Visit


def make_app():
    return create_app("testing")


def create_user(email, role_name, phone):
    user = User(email=email, phone=phone, name=role_name)
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
        "phone_primary": "01011112222",
        "date_of_birth": date(1996, 7, 1),
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return PatientService.create_patient(**data)


def create_visit(patient):
    visit = Visit(
        patient=patient,
        visit_type="gyn",
        visit_date=date(2026, 7, 13),
    )
    db.session.add(visit)
    db.session.commit()
    return visit


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


def test_create_preset_validates_name_and_sets_actor():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        doctor = create_user("doctor-preset@example.com", "Doctor", "01055110001")

        preset = PrescriptionPresetService.create_preset(
            name="Sinusitis",
            description="Common sinusitis treatment",
            actor_user=doctor,
        )

        assert preset.id is not None
        assert preset.name == "Sinusitis"
        assert preset.description == "Common sinusitis treatment"
        assert preset.created_by_user == doctor
        assert preset.updated_by_user == doctor

        with pytest.raises(ValueError, match="Preset name is required"):
            PrescriptionPresetService.create_preset(name=" ")

        db.drop_all()


def test_duplicate_preset_name_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        PrescriptionPresetService.create_preset(name="UTI")

        with pytest.raises(ValueError, match="already exists"):
            PrescriptionPresetService.create_preset(name="UTI")

        db.drop_all()


def test_update_and_deactivate_preset():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        doctor = create_user("doctor-preset-update@example.com", "Doctor", "01055110002")

        preset = PrescriptionPresetService.create_preset(name="Old Name")
        updated = PrescriptionPresetService.update_preset(
            preset,
            name="New Name",
            description="Updated description",
            is_active=False,
            actor_user=doctor,
        )

        assert updated.name == "New Name"
        assert updated.description == "Updated description"
        assert updated.is_active is False
        assert updated.updated_by_user == doctor
        assert updated not in PrescriptionPresetService.list_active_presets()

        db.drop_all()


def test_add_preset_item_requires_active_drug():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        active_drug, route = create_drug(active=True)
        inactive_drug, _inactive_route = create_drug(
            active=False,
            trade_name="Inactive",
            code_suffix="_inactive",
        )
        preset = PrescriptionPresetService.create_preset(name="Sinusitis")

        item = PrescriptionPresetService.add_item(
            preset=preset,
            drug=active_drug,
            dose="1 tablet",
            frequency="Every 24 hours",
            duration="5 days",
            instructions_ar="قرص مرة يوميًا لمدة ٥ أيام",
            route=route,
        )

        assert item.id is not None
        assert item.drug == active_drug
        assert item.route == route

        with pytest.raises(ValueError, match="Inactive drug"):
            PrescriptionPresetService.add_item(
                preset=preset,
                drug=inactive_drug,
                dose="1 tablet",
                frequency="Every 24 hours",
                duration="5 days",
                instructions_ar="تعليمات",
            )

        db.drop_all()


def test_preset_items_are_ordered_by_sort_order():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        first_drug, _route = create_drug(trade_name="Drug A", code_suffix="_a")
        second_drug, _route2 = create_drug(trade_name="Drug B", code_suffix="_b")
        preset = PrescriptionPresetService.create_preset(name="Ordered Preset")

        second = PrescriptionPresetService.add_item(
            preset=preset,
            drug=second_drug,
            dose="2 tablets",
            frequency="Every 12 hours",
            duration="7 days",
            instructions_ar="ثانيًا",
            sort_order=2,
        )
        first = PrescriptionPresetService.add_item(
            preset=preset,
            drug=first_drug,
            dose="1 tablet",
            frequency="Every 24 hours",
            duration="5 days",
            instructions_ar="أولًا",
            sort_order=1,
        )

        assert PrescriptionPresetService.list_items(preset) == [first, second]

        db.drop_all()


def test_apply_preset_adds_editable_prescription_items():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        doctor = create_user("doctor-apply-preset@example.com", "Doctor", "01055110003")
        patient = create_patient()
        visit = create_visit(patient)
        prescription = PrescriptionService.create_prescription(
            visit=visit,
            actor_user=doctor,
        )
        drug, route = create_drug()

        preset = PrescriptionPresetService.create_preset(name="Sinusitis")
        PrescriptionPresetService.add_item(
            preset=preset,
            drug=drug,
            dose="1 tablet",
            frequency="Every 24 hours",
            duration="5 days",
            instructions_ar="قرص مرة يوميًا لمدة ٥ أيام",
            route=route,
        )

        created_items = PrescriptionPresetService.apply_to_prescription(
            preset=preset,
            prescription=prescription,
            actor_user=doctor,
        )

        assert len(created_items) == 1
        assert isinstance(created_items[0], PrescriptionItem)
        assert created_items[0].prescription == prescription
        assert created_items[0].drug == drug
        assert created_items[0].dose == "1 tablet"
        assert created_items[0].instructions_ar == "قرص مرة يوميًا لمدة ٥ أيام"

        db.session.refresh(prescription)
        assert prescription.updated_by_user == doctor

        db.drop_all()


def test_apply_inactive_or_empty_preset_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        prescription = PrescriptionService.create_prescription(visit=visit)

        empty_preset = PrescriptionPresetService.create_preset(name="Empty")

        with pytest.raises(ValueError, match="no items"):
            PrescriptionPresetService.apply_to_prescription(
                preset=empty_preset,
                prescription=prescription,
            )

        inactive_preset = PrescriptionPresetService.create_preset(name="Inactive")
        PrescriptionPresetService.update_preset(inactive_preset, is_active=False)

        with pytest.raises(ValueError, match="Inactive prescription preset"):
            PrescriptionPresetService.apply_to_prescription(
                preset=inactive_preset,
                prescription=prescription,
            )

        db.drop_all()


def test_preset_permissions_for_doctor_admin_and_reception():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-preset-permission@example.com", "Doctor", "01055110004")
        admin = create_user("admin-preset-permission@example.com", "Admin", "01055110005")
        reception = create_user("reception-preset-permission@example.com", "Reception", "01055110006")

        assert RBACService.user_has_permission(doctor, "prescription_presets.manage")
        assert RBACService.user_has_permission(admin, "prescription_presets.manage")
        assert not RBACService.user_has_permission(reception, "prescription_presets.manage")

        db.drop_all()
