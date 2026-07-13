from app import create_app
from app.extensions import db
from app.models.investigation import InvestigationTest
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.settings_service import SettingsService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
    )
    return app


def test_create_investigation_category_and_test():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        category = InvestigationDictionaryService.create_category(
            code="Hormonal",
            name_en="Hormonal",
            name_ar="هرمونات",
            sort_order=1,
        )
        test = InvestigationDictionaryService.create_test(
            code="TSH",
            name_en="TSH",
            category=category,
            default_unit="mIU/L",
            default_reference_range="0.4-4.0",
            result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
        )

        assert category.code == "hormonal"
        assert test.code == "tsh"
        assert test.category == category
        assert test.default_unit == "mIU/L"

        db.drop_all()


def test_duplicate_category_code_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        InvestigationDictionaryService.create_category(code="hormonal", name_en="Hormonal")

        try:
            InvestigationDictionaryService.create_category(code="hormonal", name_en="Hormonal 2")
        except ValueError as exc:
            assert "already exists" in str(exc)
        else:
            raise AssertionError("Duplicate category code should fail")

        db.drop_all()


def test_duplicate_test_code_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        InvestigationDictionaryService.create_test(code="amh", name_en="AMH")

        try:
            InvestigationDictionaryService.create_test(code="amh", name_en="AMH 2")
        except ValueError as exc:
            assert "already exists" in str(exc)
        else:
            raise AssertionError("Duplicate test code should fail")

        db.drop_all()


def test_inactive_category_cannot_be_used_for_new_test():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        category = InvestigationDictionaryService.create_category(code="hormonal", name_en="Hormonal")
        InvestigationDictionaryService.deactivate_category(category)

        try:
            InvestigationDictionaryService.create_test(
                code="fsh",
                name_en="FSH",
                category=category,
            )
        except ValueError as exc:
            assert "Inactive category" in str(exc)
        else:
            raise AssertionError("Inactive category should fail")

        db.drop_all()


def test_list_active_tests_excludes_inactive():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        active_test = InvestigationDictionaryService.create_test(code="tsh", name_en="TSH")
        inactive_test = InvestigationDictionaryService.create_test(code="amh", name_en="AMH")
        InvestigationDictionaryService.deactivate_test(inactive_test)

        active_tests = InvestigationDictionaryService.list_active_tests()

        assert active_test in active_tests
        assert inactive_test not in active_tests

        db.drop_all()
