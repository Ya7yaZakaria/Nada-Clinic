from app.extensions import db
from app.models.drug import Drug
from app.models.prescription import Prescription, PrescriptionItem
from app.models.visit import Visit


class PrescriptionService:
    """Service layer for structured prescriptions inside visits."""

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
    def _validate_visit(visit):
        if not visit:
            raise ValueError("Visit is required")

        if not isinstance(visit, Visit):
            raise ValueError("Invalid visit")

    @staticmethod
    def _validate_drug(drug):
        if not drug:
            raise ValueError("Drug is required")

        if not isinstance(drug, Drug):
            raise ValueError("Invalid drug")

        if not drug.is_active:
            raise ValueError("Inactive drug cannot be prescribed")

    @classmethod
    def create_prescription(cls, *, visit, notes=None, actor_user=None):
        cls._validate_visit(visit)

        existing = Prescription.query.filter_by(visit_id=visit.id).first()
        if existing:
            raise ValueError("Prescription already exists for this visit")

        prescription = Prescription(
            patient_id=visit.patient_id,
            visit=visit,
            notes=cls._clean(notes) or None,
            created_by_user=actor_user,
            updated_by_user=actor_user,
        )

        db.session.add(prescription)
        db.session.commit()
        return prescription

    @staticmethod
    def get_prescription_for_visit(visit):
        if not visit:
            return None

        return Prescription.query.filter_by(visit_id=visit.id).first()

    @classmethod
    def get_or_create_prescription(cls, *, visit, notes=None, actor_user=None):
        existing = cls.get_prescription_for_visit(visit)
        if existing:
            return existing

        return cls.create_prescription(
            visit=visit,
            notes=notes,
            actor_user=actor_user,
        )

    @classmethod
    def update_prescription(cls, prescription, *, notes=None, actor_user=None):
        if not prescription:
            raise ValueError("Prescription is required")

        if notes is not None:
            prescription.notes = cls._clean(notes) or None

        if actor_user is not None:
            prescription.updated_by_user = actor_user

        db.session.commit()
        return prescription

    @classmethod
    def add_item(
        cls,
        *,
        prescription,
        drug,
        dose,
        frequency,
        duration,
        instructions_ar,
        route=None,
        sort_order=None,
    ):
        if not prescription:
            raise ValueError("Prescription is required")

        cls._validate_drug(drug)

        item = PrescriptionItem(
            prescription=prescription,
            drug=drug,
            dose=cls._require_text(dose, "Dose is required"),
            frequency=cls._require_text(frequency, "Frequency is required"),
            duration=cls._require_text(duration, "Duration is required"),
            instructions_ar=cls._require_text(instructions_ar, "Arabic instructions are required"),
            route=route if route is not None else drug.route,
            sort_order=sort_order if sort_order is not None else cls.next_sort_order(prescription),
        )

        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def next_sort_order(prescription):
        last_item = (
            PrescriptionItem.query.filter_by(prescription_id=prescription.id)
            .order_by(PrescriptionItem.sort_order.desc(), PrescriptionItem.id.desc())
            .first()
        )

        if not last_item:
            return 1

        return last_item.sort_order + 1

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
            raise ValueError("Prescription item is required")

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
            raise ValueError("Prescription item is required")

        db.session.delete(item)
        db.session.commit()

    @staticmethod
    def list_items(prescription):
        return (
            PrescriptionItem.query.filter_by(prescription_id=prescription.id)
            .order_by(PrescriptionItem.sort_order.asc(), PrescriptionItem.id.asc())
            .all()
        )
