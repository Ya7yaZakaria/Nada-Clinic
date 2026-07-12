from app.extensions import db
from app.models.drug_dictionary import (
    DrugCategory,
    DrugForm,
    DrugRoute,
    DrugSafetyStatus,
)


class DrugDictionaryService:
    DEFAULT_CATEGORIES = [
        ("antibiotic", "Antibiotic", "مضاد حيوي"),
        ("antifungal", "Antifungal", "مضاد فطريات"),
        ("analgesic", "Analgesic", "مسكن"),
        ("nsaid", "NSAID", "مضاد التهاب غير ستيرويدي"),
        ("antispasmodic", "Antispasmodic", "مضاد تقلصات"),
        ("antiemetic", "Antiemetic", "مضاد قيء"),
        ("gastrointestinal", "Gastrointestinal", "جهاز هضمي"),
        ("hormonal", "Hormonal", "هرموني"),
        ("contraceptive", "Contraceptive", "منع حمل"),
        ("ovulation_induction", "Ovulation Induction", "تنشيط تبويض"),
        ("progesterone_support", "Progesterone Support", "دعم بروجسترون"),
        ("vitamin", "Vitamin", "فيتامين"),
        ("iron", "Iron", "حديد"),
        ("calcium", "Calcium", "كالسيوم"),
        ("antihypertensive", "Antihypertensive", "خافض ضغط"),
        ("anticoagulant", "Anticoagulant", "مضاد تجلط"),
        ("thyroid", "Thyroid", "غدة درقية"),
        ("diabetes", "Diabetes", "سكر"),
        ("local_vaginal", "Local Vaginal", "علاج مهبلي موضعي"),
        ("local_skin", "Local Skin", "علاج جلدي موضعي"),
        ("other", "Other", "أخرى"),
    ]

    DEFAULT_FORMS = [
        ("tablet", "Tablet", "أقراص"),
        ("capsule", "Capsule", "كبسولات"),
        ("syrup", "Syrup", "شراب"),
        ("suspension", "Suspension", "معلق"),
        ("injection", "Injection", "حقن"),
        ("ampoule", "Ampoule", "أمبول"),
        ("vial", "Vial", "فيال"),
        ("cream", "Cream", "كريم"),
        ("ointment", "Ointment", "مرهم"),
        ("gel", "Gel", "جل"),
        ("spray", "Spray", "بخاخ"),
        ("drops", "Drops", "نقط"),
        ("suppository", "Suppository", "لبوس"),
        ("vaginal_tablet", "Vaginal Tablet", "قرص مهبلي"),
        ("vaginal_cream", "Vaginal Cream", "كريم مهبلي"),
        ("sachet", "Sachet", "كيس"),
        ("other", "Other", "أخرى"),
    ]

    DEFAULT_ROUTES = [
        ("oral", "Oral", "عن طريق الفم"),
        ("vaginal", "Vaginal", "مهبلي"),
        ("rectal", "Rectal", "شرجي"),
        ("topical", "Topical", "موضعي"),
        ("intramuscular", "Intramuscular", "حقن عضلي"),
        ("intravenous", "Intravenous", "حقن وريدي"),
        ("subcutaneous", "Subcutaneous", "تحت الجلد"),
        ("inhaled", "Inhaled", "استنشاق"),
        ("ophthalmic", "Ophthalmic", "للعين"),
        ("otic", "Otic", "للأذن"),
        ("nasal", "Nasal", "للأنف"),
        ("other", "Other", "أخرى"),
    ]

    DEFAULT_SAFETY_STATUSES = [
        ("unknown", "Unknown", "غير معروف", 0),
        ("safe", "Safe", "آمن", 1),
        ("caution", "Caution", "بحذر", 2),
        ("avoid", "Avoid", "يفضل تجنبه", 3),
        ("contraindicated", "Contraindicated", "ممنوع", 4),
    ]

    @staticmethod
    def normalize_code(value):
        return (value or "").strip().lower().replace(" ", "_")

    @classmethod
    def _validate_basic_data(cls, *, code, name_en):
        normalized_code = cls.normalize_code(code)

        if not normalized_code:
            raise ValueError("Code is required")

        if not (name_en or "").strip():
            raise ValueError("English name is required")

        return normalized_code

    @classmethod
    def _create_item(cls, model, *, code, name_en, name_ar=None, sort_order=0, **extra):
        normalized_code = cls._validate_basic_data(code=code, name_en=name_en)

        existing = model.query.filter_by(code=normalized_code).first()
        if existing:
            raise ValueError("Dictionary code already exists")

        item = model(
            code=normalized_code,
            name_en=name_en.strip(),
            name_ar=(name_ar or "").strip() or None,
            sort_order=sort_order or 0,
            **extra,
        )

        db.session.add(item)
        db.session.commit()
        return item

    @classmethod
    def _update_item(cls, item, *, code=None, name_en=None, name_ar=None, sort_order=None, is_active=None, **extra):
        if code is not None:
            normalized_code = cls._validate_basic_data(code=code, name_en=name_en or item.name_en)
            duplicate = item.__class__.query.filter(
                item.__class__.code == normalized_code,
                item.__class__.id != item.id,
            ).first()
            if duplicate:
                raise ValueError("Dictionary code already exists")
            item.code = normalized_code

        if name_en is not None:
            if not name_en.strip():
                raise ValueError("English name is required")
            item.name_en = name_en.strip()

        if name_ar is not None:
            item.name_ar = name_ar.strip() or None

        if sort_order is not None:
            item.sort_order = sort_order

        if is_active is not None:
            item.is_active = bool(is_active)

        for key, value in extra.items():
            setattr(item, key, value)

        db.session.commit()
        return item

    @staticmethod
    def _get_active(model):
        return model.query.filter_by(is_active=True).order_by(
            model.sort_order.asc(),
            model.name_en.asc(),
        ).all()

    @classmethod
    def create_category(cls, *, code, name_en, name_ar=None, sort_order=0):
        return cls._create_item(DrugCategory, code=code, name_en=name_en, name_ar=name_ar, sort_order=sort_order)

    @classmethod
    def update_category(cls, category, **kwargs):
        return cls._update_item(category, **kwargs)

    @classmethod
    def create_form(cls, *, code, name_en, name_ar=None, sort_order=0):
        return cls._create_item(DrugForm, code=code, name_en=name_en, name_ar=name_ar, sort_order=sort_order)

    @classmethod
    def update_form(cls, form, **kwargs):
        return cls._update_item(form, **kwargs)

    @classmethod
    def create_route(cls, *, code, name_en, name_ar=None, sort_order=0):
        return cls._create_item(DrugRoute, code=code, name_en=name_en, name_ar=name_ar, sort_order=sort_order)

    @classmethod
    def update_route(cls, route, **kwargs):
        return cls._update_item(route, **kwargs)

    @classmethod
    def create_safety_status(cls, *, code, name_en, name_ar=None, severity_order=0, sort_order=0):
        return cls._create_item(
            DrugSafetyStatus,
            code=code,
            name_en=name_en,
            name_ar=name_ar,
            sort_order=sort_order,
            severity_order=severity_order,
        )

    @classmethod
    def update_safety_status(cls, status, **kwargs):
        return cls._update_item(status, **kwargs)

    @staticmethod
    def deactivate_item(item):
        item.is_active = False
        db.session.commit()
        return item

    @staticmethod
    def reactivate_item(item):
        item.is_active = True
        db.session.commit()
        return item

    @classmethod
    def get_active_categories(cls):
        return cls._get_active(DrugCategory)

    @classmethod
    def get_active_forms(cls):
        return cls._get_active(DrugForm)

    @classmethod
    def get_active_routes(cls):
        return cls._get_active(DrugRoute)

    @classmethod
    def get_active_safety_statuses(cls):
        return cls._get_active(DrugSafetyStatus)

    @classmethod
    def seed_defaults(cls):
        for index, (code, name_en, name_ar) in enumerate(cls.DEFAULT_CATEGORIES):
            if not DrugCategory.query.filter_by(code=code).first():
                db.session.add(DrugCategory(code=code, name_en=name_en, name_ar=name_ar, sort_order=index))

        for index, (code, name_en, name_ar) in enumerate(cls.DEFAULT_FORMS):
            if not DrugForm.query.filter_by(code=code).first():
                db.session.add(DrugForm(code=code, name_en=name_en, name_ar=name_ar, sort_order=index))

        for index, (code, name_en, name_ar) in enumerate(cls.DEFAULT_ROUTES):
            if not DrugRoute.query.filter_by(code=code).first():
                db.session.add(DrugRoute(code=code, name_en=name_en, name_ar=name_ar, sort_order=index))

        for index, (code, name_en, name_ar, severity_order) in enumerate(cls.DEFAULT_SAFETY_STATUSES):
            if not DrugSafetyStatus.query.filter_by(code=code).first():
                db.session.add(
                    DrugSafetyStatus(
                        code=code,
                        name_en=name_en,
                        name_ar=name_ar,
                        severity_order=severity_order,
                        sort_order=index,
                    )
                )

        db.session.commit()
