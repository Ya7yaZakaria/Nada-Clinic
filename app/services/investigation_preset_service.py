from app.extensions import db
from app.models.investigation import InvestigationOrder, InvestigationOrderItem, InvestigationTest
from app.models.investigation_preset import InvestigationPreset, InvestigationPresetItem
from app.models.patient import Patient
from app.services.investigation_service import InvestigationService


class InvestigationPresetService:
    """Service layer for reusable investigation panels/workups."""

    @staticmethod
    def _clean(value):
        return (value or "").strip()

    @classmethod
    def _require_text(cls, value, message):
        cleaned = cls._clean(value)
        if not cleaned:
            raise ValueError(message)
        return cleaned

    @staticmethod
    def _validate_preset(preset):
        if not preset:
            raise ValueError("Investigation preset is required")

        if not isinstance(preset, InvestigationPreset):
            raise ValueError("Invalid investigation preset")

    @staticmethod
    def _validate_test(test):
        if not test:
            raise ValueError("Investigation test is required")

        if not isinstance(test, InvestigationTest):
            raise ValueError("Invalid investigation test")

        if not test.is_active:
            raise ValueError("Inactive investigation test cannot be used in preset")

    @staticmethod
    def _validate_order(order):
        if not order:
            raise ValueError("Investigation order is required")

        if not isinstance(order, InvestigationOrder):
            raise ValueError("Invalid investigation order")

    @staticmethod
    def _validate_patient(patient):
        if not patient:
            raise ValueError("Patient is required")

        if not isinstance(patient, Patient):
            raise ValueError("Invalid patient")

    @classmethod
    def _ensure_unique_name(cls, name, preset_id=None):
        existing = InvestigationPreset.query.filter_by(name=name).first()
        if existing and existing.id != preset_id:
            raise ValueError("Investigation preset name already exists")

    @classmethod
    def create_preset(cls, *, name, description=None, actor_user=None):
        cleaned_name = cls._require_text(name, "Preset name is required")
        cls._ensure_unique_name(cleaned_name)

        preset = InvestigationPreset(
            name=cleaned_name,
            description=cls._clean(description) or None,
            created_by_user=actor_user,
            updated_by_user=actor_user,
        )

        db.session.add(preset)
        db.session.commit()
        return preset

    @classmethod
    def update_preset(
        cls,
        preset,
        *,
        name=None,
        description=None,
        is_active=None,
        actor_user=None,
    ):
        cls._validate_preset(preset)

        if name is not None:
            cleaned_name = cls._require_text(name, "Preset name is required")
            cls._ensure_unique_name(cleaned_name, preset_id=preset.id)
            preset.name = cleaned_name

        if description is not None:
            preset.description = cls._clean(description) or None

        if is_active is not None:
            preset.is_active = bool(is_active)

        if actor_user is not None:
            preset.updated_by_user = actor_user

        db.session.commit()
        return preset

    @classmethod
    def deactivate_preset(cls, preset, *, actor_user=None):
        cls._validate_preset(preset)
        preset.is_active = False

        if actor_user is not None:
            preset.updated_by_user = actor_user

        db.session.commit()
        return preset

    @classmethod
    def reactivate_preset(cls, preset, *, actor_user=None):
        cls._validate_preset(preset)
        preset.is_active = True

        if actor_user is not None:
            preset.updated_by_user = actor_user

        db.session.commit()
        return preset

    @staticmethod
    def get_preset_by_uuid(preset_uuid):
        if not preset_uuid:
            return None

        return InvestigationPreset.query.filter_by(uuid=preset_uuid).first()

    @staticmethod
    def list_active_presets():
        return (
            InvestigationPreset.query.filter_by(is_active=True)
            .order_by(InvestigationPreset.name.asc(), InvestigationPreset.id.asc())
            .all()
        )

    @staticmethod
    def list_all_presets():
        return (
            InvestigationPreset.query.order_by(
                InvestigationPreset.is_active.desc(),
                InvestigationPreset.name.asc(),
                InvestigationPreset.id.asc(),
            )
            .all()
        )

    @staticmethod
    def next_sort_order(preset):
        last_item = (
            InvestigationPresetItem.query.filter_by(preset_id=preset.id)
            .order_by(
                InvestigationPresetItem.sort_order.desc(),
                InvestigationPresetItem.id.desc(),
            )
            .first()
        )

        if not last_item:
            return 1

        return last_item.sort_order + 1

    @classmethod
    def add_item(
        cls,
        *,
        preset,
        test,
        notes=None,
        sort_order=None,
    ):
        cls._validate_preset(preset)
        cls._validate_test(test)

        existing = InvestigationPresetItem.query.filter_by(
            preset_id=preset.id,
            test_id=test.id,
        ).first()
        if existing:
            raise ValueError("Investigation test already exists in preset")

        item = InvestigationPresetItem(
            preset=preset,
            test=test,
            notes=cls._clean(notes) or None,
            sort_order=sort_order if sort_order is not None else cls.next_sort_order(preset),
        )

        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def remove_item(item):
        if not item:
            raise ValueError("Investigation preset item is required")

        db.session.delete(item)
        db.session.commit()

    @staticmethod
    def list_items(preset):
        return (
            InvestigationPresetItem.query.filter_by(preset_id=preset.id)
            .order_by(InvestigationPresetItem.sort_order.asc(), InvestigationPresetItem.id.asc())
            .all()
        )

    @staticmethod
    def _order_has_active_test(order, test):
        return (
            InvestigationOrderItem.query.filter_by(order_id=order.id, test_id=test.id)
            .filter(InvestigationOrderItem.status != InvestigationOrderItem.STATUS_CANCELLED)
            .first()
            is not None
        )

    @classmethod
    def apply_to_order(cls, *, preset, order, actor_user=None):
        cls._validate_preset(preset)
        cls._validate_order(order)

        if not preset.is_active:
            raise ValueError("Inactive investigation preset cannot be applied")

        if order.status == InvestigationOrder.STATUS_CANCELLED:
            raise ValueError("Cannot apply preset to cancelled investigation order")

        preset_items = cls.list_items(preset)
        if not preset_items:
            raise ValueError("Investigation preset has no items")

        created_items = []

        for preset_item in preset_items:
            if cls._order_has_active_test(order, preset_item.test):
                continue

            created_item = InvestigationService.add_order_item(
                order=order,
                test=preset_item.test,
                item_notes=preset_item.notes,
            )
            created_items.append(created_item)

        if not created_items:
            raise ValueError("All preset tests already exist in this investigation order")

        return created_items

    @classmethod
    def missing_tests_for_patient(cls, *, preset, patient):
        cls._validate_preset(preset)
        cls._validate_patient(patient)

        preset_items = cls.list_items(preset)
        missing_tests = []

        for item in preset_items:
            latest = InvestigationService.get_latest_result(patient, item.test)
            if latest is None:
                missing_tests.append(item.test)

        return missing_tests
