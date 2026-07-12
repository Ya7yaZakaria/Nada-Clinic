from app import create_app
from app.extensions import db
from app.models.drug_dictionary import DrugCategory, DrugForm, DrugRoute, DrugSafetyStatus
from app.services.drug_dictionary_service import DrugDictionaryService


def make_app():
    return create_app("testing")


def test_dictionary_models_store_required_fields():
    app = make_app()

    with app.app_context():
        db.create_all()

        category = DrugCategory(code="antibiotic", name_en="Antibiotic", name_ar="مضاد حيوي")
        form = DrugForm(code="tablet", name_en="Tablet", name_ar="أقراص")
        route = DrugRoute(code="oral", name_en="Oral", name_ar="عن طريق الفم")
        status = DrugSafetyStatus(code="unknown", name_en="Unknown", name_ar="غير معروف", severity_order=0)

        db.session.add_all([category, form, route, status])
        db.session.commit()

        assert category.uuid
        assert form.uuid
        assert route.uuid
        assert status.uuid
        assert category.is_active is True
        assert status.severity_order == 0

        db.drop_all()


def test_seed_defaults_creates_all_dictionary_groups():
    app = make_app()

    with app.app_context():
        db.create_all()

        DrugDictionaryService.seed_defaults()

        assert DrugCategory.query.count() > 0
        assert DrugForm.query.count() > 0
        assert DrugRoute.query.count() > 0
        assert DrugSafetyStatus.query.count() == 5

        assert DrugSafetyStatus.query.filter_by(code="unknown").first()
        assert DrugSafetyStatus.query.filter_by(code="contraindicated").first()

        db.drop_all()


def test_active_dictionary_lists_hide_inactive_items():
    app = make_app()

    with app.app_context():
        db.create_all()

        active = DrugDictionaryService.create_category(
            code="active_category",
            name_en="Active Category",
        )
        inactive = DrugDictionaryService.create_category(
            code="inactive_category",
            name_en="Inactive Category",
        )
        DrugDictionaryService.deactivate_item(inactive)

        active_categories = DrugDictionaryService.get_active_categories()

        assert active in active_categories
        assert inactive not in active_categories

        db.drop_all()
