from app import create_app
from app.extensions import db
from app.models.investigation import InvestigationTest
from app.models.investigation_preset import InvestigationPreset, InvestigationPresetItem
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.settings_service import SettingsService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
    )
    return app


def create_test(code="amh", name="AMH"):
    category = InvestigationDictionaryService.create_category(
        code=f"{code}_category",
        name_en=f"{name} Category",
    )
    return InvestigationDictionaryService.create_test(
        code=code,
        name_en=name,
        category=category,
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def test_investigation_preset_and_item_models_can_be_created():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        test = create_test()

        preset = InvestigationPreset(
            name="Infertility Workup",
            description="Baseline infertility investigations",
        )
        item = InvestigationPresetItem(
            preset=preset,
            test=test,
            sort_order=1,
            notes="Baseline hormone",
        )

        db.session.add_all([preset, item])
        db.session.commit()

        assert preset.id is not None
        assert preset.uuid
        assert item.id is not None
        assert item.uuid
        assert item.preset == preset
        assert item.test == test
        assert preset.items.count() == 1

        db.drop_all()


def test_deleting_preset_cascades_items():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        test = create_test()
        preset = InvestigationPreset(name="PCOS Workup")
        item = InvestigationPresetItem(preset=preset, test=test, sort_order=1)

        db.session.add_all([preset, item])
        db.session.commit()

        item_id = item.id

        db.session.delete(preset)
        db.session.commit()

        assert db.session.get(InvestigationPresetItem, item_id) is None

        db.drop_all()
