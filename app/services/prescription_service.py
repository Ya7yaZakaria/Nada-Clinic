from app.extensions import db
from app.models.drug import Drug
from app.models.partner import Partner
from app.models.prescription import Prescription, PrescriptionItem
from app.models.visit import Visit


class PrescriptionService:
    """Service layer for structured prescriptions.

    Existing patient prescriptions remain Visit-based.
    Stage 10 adds partner-target prescriptions using the same PrescriptionItem rows.
    """

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
    def _validate_partner(partner):
        if not partner:
            raise ValueError("Partner is required")

        if not isinstance(partner, Partner):
            raise ValueError("Invalid partner")

        if not partner.is_active:
            raise ValueError("Inactive partner cannot receive prescription")

    @staticmethod
    def _validate_drug(drug):
        if not drug:
            raise ValueError("Drug is required")

        if not isinstance(drug, Drug):
            raise ValueError("Invalid drug")

        if not drug.is_active:
            raise ValueError("Inactive drug cannot be prescribed")

    @staticmethod
    def validate_prescription_target(prescription):
        if not prescription:
            raise ValueError("Prescription is required")

        if prescription.prescription_target not in Prescription.VALID_TARGETS:
            raise ValueError("Invalid prescription target")

        if prescription.prescription_target == Prescription.TARGET_PATIENT:
            if not prescription.visit_id:
                raise ValueError("Patient prescription requires a Visit")
            if prescription.partner_id:
                raise ValueError("Patient prescription cannot have partner_id")

        if prescription.prescription_target == Prescription.TARGET_PARTNER:
            if not prescription.partner_id:
                raise ValueError("Partner prescription requires partner_id")
            if prescription.partner.patient_id != prescription.patient_id:
                raise ValueError("Partner prescription patient mismatch")

        return True

    @staticmethod
    def get_prescription_display_target(prescription):
        if not prescription:
            return "—"
        if prescription.prescription_target == Prescription.TARGET_PARTNER:
            return f"Partner / Husband: {prescription.partner.name}"
        return "Patient"

    @classmethod
    def create_prescription(cls, *, visit, notes=None, actor_user=None):
        cls._validate_visit(visit)

        existing = Prescription.query.filter_by(
            visit_id=visit.id,
            prescription_target=Prescription.TARGET_PATIENT,
        ).first()
        if existing:
            raise ValueError("Prescription already exists for this visit")

        prescription = Prescription(
            patient_id=visit.patient_id,
            visit=visit,
            partner=None,
            prescription_target=Prescription.TARGET_PATIENT,
            notes=cls._clean(notes) or None,
            created_by_user=actor_user,
            updated_by_user=actor_user,
        )

        db.session.add(prescription)
        db.session.commit()
        return prescription

    @classmethod
    def create_partner_prescription(cls, *, partner, notes=None, actor_user=None):
        cls._validate_partner(partner)

        prescription = Prescription(
            patient_id=partner.patient_id,
            visit=None,
            partner=partner,
            prescription_target=Prescription.TARGET_PARTNER,
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

        return Prescription.query.filter_by(
            visit_id=visit.id,
            prescription_target=Prescription.TARGET_PATIENT,
        ).first()

    @staticmethod
    def get_prescription(prescription_uuid):
        if not prescription_uuid:
            return None
        return Prescription.query.filter_by(uuid=prescription_uuid).first()

    @staticmethod
    def get_partner_prescription(prescription_uuid):
        if not prescription_uuid:
            return None
        return Prescription.query.filter_by(
            uuid=prescription_uuid,
            prescription_target=Prescription.TARGET_PARTNER,
        ).first()

    @staticmethod
    def list_partner_prescriptions(partner):
        return (
            Prescription.query.filter_by(
                partner_id=partner.id,
                prescription_target=Prescription.TARGET_PARTNER,
            )
            .order_by(Prescription.created_at.desc(), Prescription.id.desc())
            .all()
        )

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

        cls.validate_prescription_target(prescription)
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

        cls.validate_prescription_target(item.prescription)

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
