from app.extensions import db
from app.models.investigation import InvestigationCategory, InvestigationTest


class InvestigationDictionaryService:
    """Service layer for investigation categories and tests."""

    @staticmethod
    def _clean(value):
        return (value or "").strip()

    @classmethod
    def _require_text(cls, value, message):
        cleaned = cls._clean(value)
        if not cleaned:
            raise ValueError(message)
        return cleaned

    @classmethod
    def _normalize_code(cls, code):
        return cls._require_text(code, "Code is required").lower().replace(" ", "_")

    @classmethod
    def create_category(
        cls,
        *,
        code,
        name_en,
        name_ar=None,
        description=None,
        sort_order=0,
    ):
        normalized_code = cls._normalize_code(code)

        existing = InvestigationCategory.query.filter_by(code=normalized_code).first()
        if existing:
            raise ValueError("Investigation category code already exists")

        category = InvestigationCategory(
            code=normalized_code,
            name_en=cls._require_text(name_en, "English category name is required"),
            name_ar=cls._clean(name_ar) or None,
            description=cls._clean(description) or None,
            sort_order=sort_order or 0,
        )

        db.session.add(category)
        db.session.commit()
        return category

    @classmethod
    def update_category(
        cls,
        category,
        *,
        name_en=None,
        name_ar=None,
        description=None,
        sort_order=None,
        is_active=None,
    ):
        if not category:
            raise ValueError("Investigation category is required")

        if name_en is not None:
            category.name_en = cls._require_text(name_en, "English category name is required")

        if name_ar is not None:
            category.name_ar = cls._clean(name_ar) or None

        if description is not None:
            category.description = cls._clean(description) or None

        if sort_order is not None:
            category.sort_order = sort_order

        if is_active is not None:
            category.is_active = bool(is_active)

        db.session.commit()
        return category

    @staticmethod
    def deactivate_category(category):
        if not category:
            raise ValueError("Investigation category is required")
        category.is_active = False
        db.session.commit()
        return category

    @staticmethod
    def reactivate_category(category):
        if not category:
            raise ValueError("Investigation category is required")
        category.is_active = True
        db.session.commit()
        return category

    @staticmethod
    def list_active_categories():
        return (
            InvestigationCategory.query.filter_by(is_active=True)
            .order_by(InvestigationCategory.sort_order.asc(), InvestigationCategory.name_en.asc())
            .all()
        )

    @classmethod
    def create_test(
        cls,
        *,
        code,
        name_en,
        category=None,
        name_ar=None,
        default_unit=None,
        default_reference_range=None,
        result_kind=InvestigationTest.RESULT_KIND_TEXT,
        sort_order=0,
    ):
        normalized_code = cls._normalize_code(code)

        existing = InvestigationTest.query.filter_by(code=normalized_code).first()
        if existing:
            raise ValueError("Investigation test code already exists")

        if result_kind not in InvestigationTest.RESULT_KINDS:
            raise ValueError("Invalid investigation result kind")

        if category is not None and not isinstance(category, InvestigationCategory):
            raise ValueError("Invalid investigation category")

        if category is not None and not category.is_active:
            raise ValueError("Inactive category cannot be used")

        test = InvestigationTest(
            code=normalized_code,
            name_en=cls._require_text(name_en, "English test name is required"),
            name_ar=cls._clean(name_ar) or None,
            category=category,
            default_unit=cls._clean(default_unit) or None,
            default_reference_range=cls._clean(default_reference_range) or None,
            result_kind=result_kind,
            sort_order=sort_order or 0,
        )

        db.session.add(test)
        db.session.commit()
        return test

    @classmethod
    def update_test(
        cls,
        test,
        *,
        name_en=None,
        category=None,
        name_ar=None,
        default_unit=None,
        default_reference_range=None,
        result_kind=None,
        sort_order=None,
        is_active=None,
    ):
        if not test:
            raise ValueError("Investigation test is required")

        if name_en is not None:
            test.name_en = cls._require_text(name_en, "English test name is required")

        if category is not None:
            if not isinstance(category, InvestigationCategory):
                raise ValueError("Invalid investigation category")
            if not category.is_active:
                raise ValueError("Inactive category cannot be used")
            test.category = category

        if name_ar is not None:
            test.name_ar = cls._clean(name_ar) or None

        if default_unit is not None:
            test.default_unit = cls._clean(default_unit) or None

        if default_reference_range is not None:
            test.default_reference_range = cls._clean(default_reference_range) or None

        if result_kind is not None:
            if result_kind not in InvestigationTest.RESULT_KINDS:
                raise ValueError("Invalid investigation result kind")
            test.result_kind = result_kind

        if sort_order is not None:
            test.sort_order = sort_order

        if is_active is not None:
            test.is_active = bool(is_active)

        db.session.commit()
        return test

    @staticmethod
    def deactivate_test(test):
        if not test:
            raise ValueError("Investigation test is required")
        test.is_active = False
        db.session.commit()
        return test

    @staticmethod
    def reactivate_test(test):
        if not test:
            raise ValueError("Investigation test is required")
        test.is_active = True
        db.session.commit()
        return test

    @staticmethod
    def list_active_tests():
        return (
            InvestigationTest.query.filter_by(is_active=True)
            .order_by(InvestigationTest.sort_order.asc(), InvestigationTest.name_en.asc())
            .all()
        )
