from app.extensions import db
from app.models import ClinicUltrasoundExam, Journey, Patient, Visit


class ClinicUltrasoundService:
    """Service layer for structured clinic ultrasound records."""

    @staticmethod
    def _clean(value):
        return (value or "").strip()

    @staticmethod
    def _validate_visit(visit):
        if not visit:
            raise ValueError("Visit is required")
        if not isinstance(visit, Visit):
            raise ValueError("Invalid visit")
        if not visit.patient:
            raise ValueError("Visit patient is required")

    @staticmethod
    def _validate_patient(patient):
        if not patient:
            raise ValueError("Patient is required")
        if not isinstance(patient, Patient):
            raise ValueError("Invalid patient")

    @staticmethod
    def _validate_journey(journey):
        if journey is not None and not isinstance(journey, Journey):
            raise ValueError("Invalid journey")

    @staticmethod
    def validate_exam_type(exam_type):
        exam_type = (exam_type or "").strip()
        if exam_type not in ClinicUltrasoundExam.EXAM_TYPES:
            raise ValueError("Invalid ultrasound exam type")
        return exam_type

    @staticmethod
    def validate_exam_route(exam_route):
        exam_route = (exam_route or ClinicUltrasoundExam.ROUTE_UNKNOWN).strip()
        if exam_route not in ClinicUltrasoundExam.EXAM_ROUTES:
            raise ValueError("Invalid ultrasound exam route")
        return exam_route

    @staticmethod
    def _normalize_findings_json(findings_json):
        if findings_json is None:
            return {}
        if not isinstance(findings_json, dict):
            raise ValueError("Ultrasound findings must be a dictionary")
        return findings_json

    @classmethod
    def create_exam(
        cls,
        *,
        visit,
        exam_type,
        exam_route=ClinicUltrasoundExam.ROUTE_UNKNOWN,
        findings_json=None,
        findings_text=None,
        extra_note=None,
        impression=None,
        sketch_note=None,
        actor_user=None,
    ):
        cls._validate_visit(visit)

        exam = ClinicUltrasoundExam(
            patient=visit.patient,
            visit=visit,
            journey=visit.journey,
            exam_type=cls.validate_exam_type(exam_type),
            exam_route=cls.validate_exam_route(exam_route),
            findings_json=cls._normalize_findings_json(findings_json),
            findings_text=cls._clean(findings_text) or None,
            extra_note=cls._clean(extra_note) or None,
            impression=cls._clean(impression) or None,
            sketch_note=cls._clean(sketch_note) or None,
            created_by_user=actor_user,
            is_active=True,
        )

        db.session.add(exam)
        db.session.commit()
        return exam

    @classmethod
    def update_exam(
        cls,
        exam,
        *,
        exam_type=None,
        exam_route=None,
        findings_json=None,
        findings_text=None,
        extra_note=None,
        impression=None,
        sketch_note=None,
    ):
        if not exam:
            raise ValueError("Ultrasound exam is required")
        if not isinstance(exam, ClinicUltrasoundExam):
            raise ValueError("Invalid ultrasound exam")
        if not exam.is_active:
            raise ValueError("Cannot update archived ultrasound exam")

        if exam_type is not None:
            exam.exam_type = cls.validate_exam_type(exam_type)

        if exam_route is not None:
            exam.exam_route = cls.validate_exam_route(exam_route)

        if findings_json is not None:
            exam.findings_json = cls._normalize_findings_json(findings_json)

        if findings_text is not None:
            exam.findings_text = cls._clean(findings_text) or None

        if extra_note is not None:
            exam.extra_note = cls._clean(extra_note) or None

        if impression is not None:
            exam.impression = cls._clean(impression) or None

        if sketch_note is not None:
            exam.sketch_note = cls._clean(sketch_note) or None

        db.session.commit()
        return exam

    @staticmethod
    def get_exam(exam_uuid, include_inactive=False):
        query = ClinicUltrasoundExam.query.filter_by(uuid=exam_uuid)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.first()

    @classmethod
    def list_visit_exams(cls, visit, *, include_inactive=False):
        cls._validate_visit(visit)

        query = ClinicUltrasoundExam.query.filter_by(visit_id=visit.id)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.order_by(
            ClinicUltrasoundExam.created_at.desc(),
            ClinicUltrasoundExam.id.desc(),
        ).all()

    @classmethod
    def list_patient_exams(cls, patient, *, include_inactive=False):
        cls._validate_patient(patient)

        query = ClinicUltrasoundExam.query.filter_by(patient_id=patient.id)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return (
            query.join(Visit, ClinicUltrasoundExam.visit_id == Visit.id)
            .order_by(Visit.visit_date.desc(), ClinicUltrasoundExam.id.desc())
            .all()
        )

    @staticmethod
    def archive_exam(exam, actor_user=None):
        if not exam:
            raise ValueError("Ultrasound exam is required")

        if not exam.is_active:
            return exam

        exam.is_active = False
        db.session.commit()
        return exam

    @classmethod
    def build_summary(cls, exam):
        if not exam:
            return ""

        parts = []

        if exam.exam_type:
            parts.append(exam.exam_type.upper().replace("_", "/"))

        if cls._clean(exam.impression):
            parts.append(cls._clean(exam.impression))
        elif cls._clean(exam.findings_text):
            parts.append(cls._clean(exam.findings_text))

        return " — ".join(parts)
