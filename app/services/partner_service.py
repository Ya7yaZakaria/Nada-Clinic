from app.extensions import db
from app.models.partner import Partner


class PartnerService:
    """Service layer for patient-linked partner records."""

    @staticmethod
    def _clean(value):
        return (value or "").strip()

    @staticmethod
    def _clean_or_none(value):
        cleaned = PartnerService._clean(value)
        return cleaned or None

    @staticmethod
    def get_partner(partner_uuid):
        if not partner_uuid:
            return None
        return Partner.query.filter_by(uuid=partner_uuid, is_active=True).first()

    @staticmethod
    def get_patient_partner(patient):
        if not patient:
            return None
        return (
            Partner.query.filter_by(patient_id=patient.id, is_active=True)
            .order_by(Partner.created_at.desc(), Partner.id.desc())
            .first()
        )

    @staticmethod
    def list_patient_partners(patient, include_inactive=False):
        query = Partner.query.filter_by(patient_id=patient.id)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Partner.created_at.desc(), Partner.id.desc()).all()

    @staticmethod
    def validate_one_active_partner(patient, exclude_partner=None):
        query = Partner.query.filter_by(patient_id=patient.id, is_active=True)
        if exclude_partner is not None:
            query = query.filter(Partner.id != exclude_partner.id)
        if query.first():
            raise ValueError("Patient already has an active partner record.")

    @staticmethod
    def validate_required(patient, name):
        if not patient:
            raise ValueError("Patient is required.")
        if not PartnerService._clean(name):
            raise ValueError("Partner name is required.")

    @staticmethod
    def create_partner(
        *,
        patient,
        name,
        phone=None,
        age_years=None,
        occupation=None,
        previous_children=None,
        fertility_notes=None,
        medical_notes=None,
        follow_up_note=None,
        follow_up_date=None,
    ):
        PartnerService.validate_required(patient, name)
        PartnerService.validate_one_active_partner(patient)

        partner = Partner(
            patient=patient,
            name=PartnerService._clean(name),
            phone=PartnerService._clean_or_none(phone),
            age_years=age_years,
            occupation=PartnerService._clean_or_none(occupation),
            previous_children=PartnerService._clean_or_none(previous_children),
            fertility_notes=PartnerService._clean_or_none(fertility_notes),
            medical_notes=PartnerService._clean_or_none(medical_notes),
            follow_up_note=PartnerService._clean_or_none(follow_up_note),
            follow_up_date=follow_up_date,
            is_active=True,
        )
        db.session.add(partner)
        db.session.commit()
        return partner

    @staticmethod
    def update_partner(
        partner,
        *,
        name,
        phone=None,
        age_years=None,
        occupation=None,
        previous_children=None,
        fertility_notes=None,
        medical_notes=None,
        follow_up_note=None,
        follow_up_date=None,
    ):
        if not partner:
            raise ValueError("Partner is required.")

        PartnerService.validate_required(partner.patient, name)
        PartnerService.validate_one_active_partner(partner.patient, exclude_partner=partner)

        partner.name = PartnerService._clean(name)
        partner.phone = PartnerService._clean_or_none(phone)
        partner.age_years = age_years
        partner.occupation = PartnerService._clean_or_none(occupation)
        partner.previous_children = PartnerService._clean_or_none(previous_children)
        partner.fertility_notes = PartnerService._clean_or_none(fertility_notes)
        partner.medical_notes = PartnerService._clean_or_none(medical_notes)
        partner.follow_up_note = PartnerService._clean_or_none(follow_up_note)
        partner.follow_up_date = follow_up_date

        db.session.commit()
        return partner

    @staticmethod
    def archive_partner(partner):
        if not partner:
            raise ValueError("Partner is required.")

        partner.is_active = False
        db.session.commit()
        return partner
