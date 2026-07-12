from sqlalchemy import or_

from app.extensions import db
from app.models.drug import Drug


_UNSET = object()


class DrugService:
    """Service layer for clinic drug database."""

    @staticmethod
    def _clean(value):
        return (value or "").strip()

    @classmethod
    def _validate_required(cls, *, generic_name, trade_name, strength, form):
        if not cls._clean(generic_name):
            raise ValueError("Generic name is required")

        if not cls._clean(trade_name):
            raise ValueError("Trade name is required")

        if not cls._clean(strength):
            raise ValueError("Strength is required")

        if not form:
            raise ValueError("Drug form is required")

    @classmethod
    def _find_duplicate(cls, *, trade_name, form_id, strength, exclude_id=None):
        query = Drug.query.filter(
            Drug.trade_name == cls._clean(trade_name),
            Drug.form_id == form_id,
            Drug.strength == cls._clean(strength),
        )

        if exclude_id is not None:
            query = query.filter(Drug.id != exclude_id)

        return query.first()

    @classmethod
    def create_drug(
        cls,
        *,
        generic_name,
        trade_name,
        strength,
        form,
        category=None,
        route=None,
        pregnancy_status=None,
        pregnancy_note=None,
        lactation_status=None,
        lactation_note=None,
        doctor_notes=None,
    ):
        cls._validate_required(
            generic_name=generic_name,
            trade_name=trade_name,
            strength=strength,
            form=form,
        )

        duplicate = cls._find_duplicate(
            trade_name=trade_name,
            form_id=form.id,
            strength=strength,
        )
        if duplicate:
            raise ValueError("Drug already exists with the same trade name, form, and strength")

        drug = Drug(
            generic_name=cls._clean(generic_name),
            trade_name=cls._clean(trade_name),
            strength=cls._clean(strength),
            category=category,
            form=form,
            route=route,
            pregnancy_status=pregnancy_status,
            pregnancy_note=cls._clean(pregnancy_note) or None,
            lactation_status=lactation_status,
            lactation_note=cls._clean(lactation_note) or None,
            doctor_notes=cls._clean(doctor_notes) or None,
        )

        db.session.add(drug)
        db.session.commit()
        return drug

    @classmethod
    def update_drug(
        cls,
        drug,
        *,
        generic_name=None,
        trade_name=None,
        strength=None,
        form=None,
        category=_UNSET,
        route=_UNSET,
        pregnancy_status=_UNSET,
        pregnancy_note=None,
        lactation_status=_UNSET,
        lactation_note=None,
        doctor_notes=None,
        is_active=None,
    ):
        next_generic_name = cls._clean(generic_name) if generic_name is not None else drug.generic_name
        next_trade_name = cls._clean(trade_name) if trade_name is not None else drug.trade_name
        next_strength = cls._clean(strength) if strength is not None else drug.strength
        next_form = form if form is not None else drug.form

        cls._validate_required(
            generic_name=next_generic_name,
            trade_name=next_trade_name,
            strength=next_strength,
            form=next_form,
        )

        duplicate = cls._find_duplicate(
            trade_name=next_trade_name,
            form_id=next_form.id,
            strength=next_strength,
            exclude_id=drug.id,
        )
        if duplicate:
            raise ValueError("Drug already exists with the same trade name, form, and strength")

        drug.generic_name = next_generic_name
        drug.trade_name = next_trade_name
        drug.strength = next_strength
        drug.form = next_form

        if category is not _UNSET:
            drug.category = category

        if route is not _UNSET:
            drug.route = route

        if pregnancy_status is not _UNSET:
            drug.pregnancy_status = pregnancy_status

        if pregnancy_note is not None:
            drug.pregnancy_note = cls._clean(pregnancy_note) or None

        if lactation_status is not _UNSET:
            drug.lactation_status = lactation_status

        if lactation_note is not None:
            drug.lactation_note = cls._clean(lactation_note) or None

        if doctor_notes is not None:
            drug.doctor_notes = cls._clean(doctor_notes) or None

        if is_active is not None:
            drug.is_active = bool(is_active)

        db.session.commit()
        return drug

    @staticmethod
    def deactivate_drug(drug):
        drug.is_active = False
        db.session.commit()
        return drug

    @staticmethod
    def reactivate_drug(drug):
        drug.is_active = True
        db.session.commit()
        return drug

    @staticmethod
    def get_active_drugs():
        return Drug.query.filter_by(is_active=True).order_by(
            Drug.trade_name.asc(),
            Drug.strength.asc(),
        ).all()

    @classmethod
    def search_drugs(cls, query_text):
        query_text = cls._clean(query_text)

        if not query_text:
            return cls.get_active_drugs()

        pattern = f"%{query_text}%"

        return Drug.query.filter(
            Drug.is_active.is_(True),
            or_(
                Drug.trade_name.ilike(pattern),
                Drug.generic_name.ilike(pattern),
                Drug.strength.ilike(pattern),
            ),
        ).order_by(
            Drug.trade_name.asc(),
            Drug.strength.asc(),
        ).all()
