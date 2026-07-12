from datetime import date

from app import create_app
from app.extensions import db
from app.models.drug import Drug
from app.models.drug_dictionary import DrugForm, DrugRoute
from app.models.patient import Patient
from app.models.prescription_preset import PrescriptionPreset, PrescriptionPresetItem
from app.services.patient_service import PatientService
from app.services.settings_service import SettingsService


def make_app():
    return create_app("testing")


def create_drug():
    form = DrugForm(code="tablet", name_en="Tablet")
    route = DrugRoute(code="oral", name_en="Oral")
    db.session.add_all([form, route])
    db.session.commit()

    drug = Drug(
        generic_name="Levofloxacin",
        trade_name="Tavanic",
        strength="500 mg",
        form=form,
        route=route,
    )
    db.session.add(drug)
    db.session.commit()

    return drug, route


def test_prescription_preset_can_be_created():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        preset = PrescriptionPreset(
            name="Sinusitis",
            description="Common sinusitis preset",
        )
        db.session.add(preset)
        db.session.commit()

        assert preset.id is not None
        assert preset.uuid
        assert preset.name == "Sinusitis"
        assert preset.is_active is True

        db.drop_all()


def test_prescription_preset_item_can_be_created():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        drug, route = create_drug()

        preset = PrescriptionPreset(name="Sinusitis")
        db.session.add(preset)
        db.session.commit()

        item = PrescriptionPresetItem(
            preset=preset,
            drug=drug,
            dose="1 tablet",
            frequency="Every 24 hours",
            duration="5 days",
            instructions_ar="قرص مرة يوميًا لمدة ٥ أيام بعد الأكل",
            route=route,
            sort_order=1,
        )
        db.session.add(item)
        db.session.commit()

        assert item.id is not None
        assert item.uuid
        assert item.preset == preset
        assert item.drug == drug
        assert item.route == route
        assert item.instructions_ar == "قرص مرة يوميًا لمدة ٥ أيام بعد الأكل"

        db.drop_all()


def test_deleting_preset_cascades_items():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        drug, route = create_drug()

        preset = PrescriptionPreset(name="UTI")
        db.session.add(preset)
        db.session.commit()

        item = PrescriptionPresetItem(
            preset=preset,
            drug=drug,
            dose="1 tablet",
            frequency="Every 12 hours",
            duration="7 days",
            instructions_ar="تعليمات",
            route=route,
            sort_order=1,
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

        db.session.delete(preset)
        db.session.commit()

        assert db.session.get(PrescriptionPresetItem, item_id) is None

        db.drop_all()


def test_preset_name_database_unique_constraint():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        first = PrescriptionPreset(name="BV")
        db.session.add(first)
        db.session.commit()

        second = PrescriptionPreset(name="BV")
        db.session.add(second)

        try:
            db.session.commit()
            assert False, "Expected unique preset name failure"
        except Exception:
            db.session.rollback()

        db.drop_all()
