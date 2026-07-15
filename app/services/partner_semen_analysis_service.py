from app.extensions import db
from app.models import PatientDocument
from app.models.partner import PartnerSemenAnalysis
from app.services.document_service import DocumentService


class PartnerSemenAnalysisService:
    """Simple SA history service: date + notes + optional uploaded document."""

    @staticmethod
    def _clean_or_none(value):
        cleaned = (value or "").strip()
        return cleaned or None

    @staticmethod
    def get_analysis(sa_uuid):
        if not sa_uuid:
            return None
        return PartnerSemenAnalysis.query.filter_by(uuid=sa_uuid, is_active=True).first()

    @staticmethod
    def list_partner_analyses(partner, include_inactive=False):
        query = PartnerSemenAnalysis.query.filter_by(partner_id=partner.id)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(
            PartnerSemenAnalysis.analysis_date.desc(),
            PartnerSemenAnalysis.id.desc(),
        ).all()

    @staticmethod
    def latest_for_partner(partner):
        if not partner:
            return None
        return (
            PartnerSemenAnalysis.query.filter_by(partner_id=partner.id, is_active=True)
            .order_by(PartnerSemenAnalysis.analysis_date.desc(), PartnerSemenAnalysis.id.desc())
            .first()
        )

    @staticmethod
    def create_analysis(*, partner, analysis_date, notes=None, file_storage=None, actor_user=None):
        if not partner:
            raise ValueError("Partner is required.")
        if not analysis_date:
            raise ValueError("Semen analysis date is required.")

        document = None
        if file_storage and getattr(file_storage, "filename", ""):
            document = DocumentService.save_uploaded_file(
                patient=partner.patient,
                file_storage=file_storage,
                document_type=PatientDocument.TYPE_SEMEN_ANALYSIS,
                title=f"Semen analysis - {analysis_date.isoformat()}",
                description=notes,
                actor_user=actor_user,
            )

        analysis = PartnerSemenAnalysis(
            partner=partner,
            patient=partner.patient,
            analysis_date=analysis_date,
            notes=PartnerSemenAnalysisService._clean_or_none(notes),
            document=document,
            created_by_user=actor_user,
            is_active=True,
        )
        db.session.add(analysis)
        db.session.commit()
        return analysis

    @staticmethod
    def archive_analysis(analysis):
        if not analysis:
            raise ValueError("Semen analysis is required.")

        analysis.is_active = False
        db.session.commit()
        return analysis
