from datetime import datetime, timezone

from app.extensions import db
from app.models import ExternalUltrasoundRequest, Patient, PatientDocument, Visit


class ExternalUltrasoundService:
    """Service layer for lightweight external ultrasound request/result tracking."""

    DIRECT_RESULT_NOTE = "Direct external ultrasound result"

    @staticmethod
    def _clean(value):
        return (value or "").strip()

    @staticmethod
    def _clean_list(values):
        if not values:
            return []

        cleaned = []

        for value in values:
            item = (value or "").strip()
            if item and item not in cleaned:
                cleaned.append(item)

        return cleaned

    @staticmethod
    def _require_text(value, message):
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError(message)
        return cleaned

    @staticmethod
    def _validate_patient(patient):
        if not patient:
            raise ValueError("Patient is required")
        if not isinstance(patient, Patient):
            raise ValueError("Invalid patient")

    @staticmethod
    def _validate_visit(visit):
        if not visit:
            raise ValueError("Visit is required")
        if not isinstance(visit, Visit):
            raise ValueError("Invalid visit")
        if not visit.patient:
            raise ValueError("Visit patient is required")

    @staticmethod
    def _validate_document(document):
        if not document:
            raise ValueError("Result document is required")
        if not isinstance(document, PatientDocument):
            raise ValueError("Invalid result document")

    @staticmethod
    def _validate_request(request):
        if not request:
            raise ValueError("External ultrasound request is required")
        if not isinstance(request, ExternalUltrasoundRequest):
            raise ValueError("Invalid external ultrasound request")

    @classmethod
    def create_request(
        cls,
        *,
        visit,
        request_note,
        categories=None,
        modalities=None,
        actor_user=None,
    ):
        cls._validate_visit(visit)

        request = ExternalUltrasoundRequest(
            patient=visit.patient,
            requested_visit=visit,
            request_note=cls._require_text(
                request_note,
                "External ultrasound request note is required",
            ),
            request_categories_json=cls._clean_list(categories),
            request_modalities_json=cls._clean_list(modalities),
            status=ExternalUltrasoundRequest.STATUS_PENDING,
            created_by_user=actor_user,
        )

        db.session.add(request)
        db.session.commit()
        return request

    @classmethod
    def cancel_request(cls, request):
        cls._validate_request(request)

        if request.status == ExternalUltrasoundRequest.STATUS_COMPLETED:
            raise ValueError("Cannot cancel completed external ultrasound request")

        if request.status == ExternalUltrasoundRequest.STATUS_CANCELLED:
            return request

        request.status = ExternalUltrasoundRequest.STATUS_CANCELLED
        db.session.commit()
        return request

    @classmethod
    def _complete_request(
        cls,
        *,
        request,
        result_visit,
        result_document=None,
        result_note=None,
        actor_user=None,
    ):
        cls._validate_request(request)
        cls._validate_visit(result_visit)

        cleaned_note = cls._clean(result_note)

        if not result_document and not cleaned_note:
            raise ValueError("External ultrasound result requires a file or a doctor review note")

        if request.status == ExternalUltrasoundRequest.STATUS_CANCELLED:
            raise ValueError("Cannot complete cancelled external ultrasound request")

        if request.status == ExternalUltrasoundRequest.STATUS_COMPLETED:
            raise ValueError("External ultrasound request is already completed")

        if result_visit.patient_id != request.patient_id:
            raise ValueError("Result visit does not belong to request patient")

        if result_document:
            cls._validate_document(result_document)
            if result_document.patient_id != request.patient_id:
                raise ValueError("Result document does not belong to request patient")

        request.result_visit = result_visit
        request.result_document = result_document
        request.result_note = cleaned_note or None
        request.status = ExternalUltrasoundRequest.STATUS_COMPLETED
        request.completed_by_user = actor_user
        request.completed_at = datetime.now(timezone.utc)

        db.session.commit()
        return request

    @classmethod
    def complete_request_with_document(
        cls,
        *,
        request,
        result_visit,
        result_document,
        result_note=None,
        actor_user=None,
    ):
        return cls._complete_request(
            request=request,
            result_visit=result_visit,
            result_document=result_document,
            result_note=result_note,
            actor_user=actor_user,
        )

    @classmethod
    def complete_request_with_note(
        cls,
        *,
        request,
        result_visit,
        result_note,
        actor_user=None,
    ):
        return cls._complete_request(
            request=request,
            result_visit=result_visit,
            result_document=None,
            result_note=result_note,
            actor_user=actor_user,
        )

    @classmethod
    def create_direct_result(
        cls,
        *,
        visit,
        result_document=None,
        result_note=None,
        categories=None,
        modalities=None,
        actor_user=None,
    ):
        cls._validate_visit(visit)
        cleaned_note = cls._clean(result_note)

        if not result_document and not cleaned_note:
            raise ValueError("External ultrasound result requires a file or a doctor review note")

        if result_document:
            cls._validate_document(result_document)
            if result_document.patient_id != visit.patient_id:
                raise ValueError("Result document does not belong to visit patient")

        request = ExternalUltrasoundRequest(
            patient=visit.patient,
            requested_visit=visit,
            result_visit=visit,
            request_note=cleaned_note or cls.DIRECT_RESULT_NOTE,
            request_categories_json=cls._clean_list(categories),
            request_modalities_json=cls._clean_list(modalities),
            status=ExternalUltrasoundRequest.STATUS_COMPLETED,
            result_document=result_document,
            result_note=cleaned_note or None,
            created_by_user=actor_user,
            completed_by_user=actor_user,
            completed_at=datetime.now(timezone.utc),
        )

        db.session.add(request)
        db.session.commit()
        return request

    @classmethod
    def get_request(cls, request_uuid, *, include_cancelled=False):
        query = ExternalUltrasoundRequest.query.filter_by(uuid=request_uuid)

        if not include_cancelled:
            query = query.filter(
                ExternalUltrasoundRequest.status != ExternalUltrasoundRequest.STATUS_CANCELLED
            )

        return query.first()

    @classmethod
    def list_pending_for_patient(cls, patient):
        cls._validate_patient(patient)

        return (
            ExternalUltrasoundRequest.query.filter_by(
                patient_id=patient.id,
                status=ExternalUltrasoundRequest.STATUS_PENDING,
            )
            .order_by(
                ExternalUltrasoundRequest.created_at.asc(),
                ExternalUltrasoundRequest.id.asc(),
            )
            .all()
        )

    @classmethod
    def list_visit_requests(cls, visit):
        cls._validate_visit(visit)

        return (
            ExternalUltrasoundRequest.query.filter_by(requested_visit_id=visit.id)
            .order_by(
                ExternalUltrasoundRequest.created_at.desc(),
                ExternalUltrasoundRequest.id.desc(),
            )
            .all()
        )

    @classmethod
    def list_visit_results(cls, visit):
        cls._validate_visit(visit)

        return (
            ExternalUltrasoundRequest.query.filter_by(
                result_visit_id=visit.id,
                status=ExternalUltrasoundRequest.STATUS_COMPLETED,
            )
            .order_by(
                ExternalUltrasoundRequest.completed_at.desc(),
                ExternalUltrasoundRequest.id.desc(),
            )
            .all()
        )

    @classmethod
    def list_patient_requests(cls, patient, *, include_cancelled=False):
        cls._validate_patient(patient)

        query = ExternalUltrasoundRequest.query.filter_by(patient_id=patient.id)

        if not include_cancelled:
            query = query.filter(
                ExternalUltrasoundRequest.status != ExternalUltrasoundRequest.STATUS_CANCELLED
            )

        return query.order_by(
            ExternalUltrasoundRequest.created_at.desc(),
            ExternalUltrasoundRequest.id.desc(),
        ).all()

    @classmethod
    def list_patient_results(cls, patient):
        cls._validate_patient(patient)

        return (
            ExternalUltrasoundRequest.query.filter_by(
                patient_id=patient.id,
                status=ExternalUltrasoundRequest.STATUS_COMPLETED,
            )
            .order_by(
                ExternalUltrasoundRequest.completed_at.desc(),
                ExternalUltrasoundRequest.id.desc(),
            )
            .all()
        )
