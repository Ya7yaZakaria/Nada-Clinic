from app.extensions import db
from app.models.drug import Drug
from app.models.prescription import Prescription
from app.models.prescription_preset import PrescriptionPreset, PrescriptionPresetItem
from app.services.prescription_service import PrescriptionService


class PrescriptionPresetService:
    """Service layer for reusable structured prescription presets."""

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
    def _validate_drug(drug):
        if not drug:
            raise ValueError("Drug is required")

        if not isinstance(drug, Drug):
            raise ValueError("Invalid drug")

        if not drug.is_active:
            raise ValueError("Inactive drug cannot be used in preset")

    @staticmethod
    def _validate_preset(preset):
        if not preset:
            raise ValueError("Preset is required")

        if not isinstance(preset, PrescriptionPreset):
            raise ValueError("Invalid preset")

    @staticmethod
    def _validate_prescription(prescription):
        if not prescription:
            raise ValueError("Prescription is required")

        if not isinstance(prescription, Prescription):
            raise ValueError("Invalid prescription")

    @classmethod
    def _ensure_unique_name(cls, name, preset_id=None):
        existing = PrescriptionPreset.query.filter_by(name=name).first()
        if existing and existing.id != preset_id:
            raise ValueError("Prescription preset name already exists")

    @classmethod
    def create_preset(cls, *, name, description=None, actor_user=None):
        cleaned_name = cls._require_text(name, "Preset name is required")
        cls._ensure_unique_name(cleaned_name)

        preset = PrescriptionPreset(
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

    @staticmethod
    def get_preset_by_uuid(preset_uuid):
        if not preset_uuid:
            return None

        return PrescriptionPreset.query.filter_by(uuid=preset_uuid).first()

    @staticmethod
    def list_active_presets():
        return (
            PrescriptionPreset.query.filter_by(is_active=True)
            .order_by(PrescriptionPreset.name.asc(), PrescriptionPreset.id.asc())
            .all()
        )

    @staticmethod
    def list_all_presets():
        return (
            PrescriptionPreset.query.order_by(
                PrescriptionPreset.is_active.desc(),
                PrescriptionPreset.name.asc(),
                PrescriptionPreset.id.asc(),
            )
            .all()
        )

    @classmethod
    def add_item(
        cls,
        *,
        preset,
        drug,
        dose,
        frequency,
        duration,
        instructions_ar,
        route=None,
        sort_order=None,
    ):
        cls._validate_preset(preset)
        cls._validate_drug(drug)

        item = PrescriptionPresetItem(
            preset=preset,
            drug=drug,
            dose=cls._require_text(dose, "Dose is required"),
            frequency=cls._require_text(frequency, "Frequency is required"),
            duration=cls._require_text(duration, "Duration is required"),
            instructions_ar=cls._require_text(instructions_ar, "Arabic instructions are required"),
            route=route if route is not None else drug.route,
            sort_order=sort_order if sort_order is not None else cls.next_sort_order(preset),
        )

        db.session.add(item)
        db.session.commit()
        return item

    @classmethod
    def update_item(
        cls,
        item,
        *,
        drug=None,
        dose=None,
        frequency=None,
        duration=None,
        instructions_ar=None,
        route=None,
        sort_order=None,
    ):
        if not item:
            raise ValueError("Preset item is required")

        if drug is not None:
            cls._validate_drug(drug)
            item.drug = drug

        if dose is not None:
            item.dose = cls._require_text(dose, "Dose is required")

        if frequency is not None:
            item.frequency = cls._require_text(frequency, "Frequency is required")

        if duration is not None:
            item.duration = cls._require_text(duration, "Duration is required")

        if instructions_ar is not None:
            item.instructions_ar = cls._require_text(
                instructions_ar,
                "Arabic instructions are required",
            )

        if route is not None:
            item.route = route

        if sort_order is not None:
            item.sort_order = sort_order

        db.session.commit()
        return item

    @staticmethod
    def remove_item(item):
        if not item:
            raise ValueError("Preset item is required")

        db.session.delete(item)
        db.session.commit()

    @staticmethod
    def list_items(preset):
        return (
            PrescriptionPresetItem.query.filter_by(preset_id=preset.id)
            .order_by(PrescriptionPresetItem.sort_order.asc(), PrescriptionPresetItem.id.asc())
            .all()
        )

    @staticmethod
    def next_sort_order(preset):
        last_item = (
            PrescriptionPresetItem.query.filter_by(preset_id=preset.id)
            .order_by(PrescriptionPresetItem.sort_order.desc(), PrescriptionPresetItem.id.desc())
            .first()
        )

        if not last_item:
            return 1

        return last_item.sort_order + 1

    @classmethod
    def apply_to_prescription(cls, *, preset, prescription, actor_user=None):
        cls._validate_preset(preset)
        cls._validate_prescription(prescription)

        if not preset.is_active:
            raise ValueError("Inactive prescription preset cannot be applied")

        preset_items = cls.list_items(preset)
        if not preset_items:
            raise ValueError("Prescription preset has no items")

        created_items = []
        for preset_item in preset_items:
            created_item = PrescriptionService.add_item(
                prescription=prescription,
                drug=preset_item.drug,
                dose=preset_item.dose,
                frequency=preset_item.frequency,
                duration=preset_item.duration,
                instructions_ar=preset_item.instructions_ar,
                route=preset_item.route,
            )
            created_items.append(created_item)

        PrescriptionService.update_prescription(
            prescription,
            actor_user=actor_user,
        )

        return created_items
