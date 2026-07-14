from datetime import date

from app import create_app
from app.extensions import db
from app.models import ClinicUltrasoundExam, ExternalUltrasoundRequest, PatientDocument
from app.services.patient_service import PatientService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_patient(phone="01088880100"):
    return PatientService.create_patient(
        name_ar="منى علي",
        name_en="Mona Ali",
        phone_primary=phone,
        date_of_birth=date(1996, 7, 1),
    )


def test_clinic_ultrasound_model_links_visit_and_uses_visit_date():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient()
        visit = VisitService.create_visit(patient=patient, visit_type="obs")

        exam = ClinicUltrasoundExam(
            patient=patient,
            visit=visit,
            journey=visit.journey,
            exam_type=ClinicUltrasoundExam.EXAM_TYPE_OBS,
            exam_route=ClinicUltrasoundExam.ROUTE_TRANSABDOMINAL,
            findings_json={"presentation": "cephalic"},
            findings_text="Single viable cephalic fetus.",
            sketch_note="Placenta fundal anterior.",
        )

        db.session.add(exam)
        db.session.commit()

        assert exam.id is not None
        assert exam.patient_id == patient.id
        assert exam.visit_id == visit.id
        assert exam.exam_date == visit.visit_date
        assert "exam_date" not in ClinicUltrasoundExam.__table__.columns
        assert exam.findings_json["presentation"] == "cephalic"
        assert exam.is_active is True

        db.drop_all()


def test_external_ultrasound_request_model_can_link_result_document():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone="01088880101")
        requested_visit = VisitService.create_visit(patient=patient, visit_type="obs")
        result_visit = VisitService.create_visit(patient=patient, visit_type="obs")

        document = PatientDocument(
            patient=patient,
            visit=result_visit,
            document_type=PatientDocument.TYPE_ULTRASOUND_REPORT,
            title="External ultrasound report",
            description="Report notes",
            original_filename="us.pdf",
            stored_filename="us.pdf",
            storage_path="/tmp/us.pdf",
            mime_type="application/pdf",
            file_size=10,
            is_active=True,
        )

        request = ExternalUltrasoundRequest(
            patient=patient,
            requested_visit=requested_visit,
            result_visit=result_visit,
            result_document=document,
            request_note="Growth scan + Doppler outside.",
            status=ExternalUltrasoundRequest.STATUS_COMPLETED,
        )

        db.session.add(document)
        db.session.add(request)
        db.session.commit()

        assert request.id is not None
        assert request.patient_id == patient.id
        assert request.requested_visit_id == requested_visit.id
        assert request.result_visit_id == result_visit.id
        assert request.result_document_id == document.id
        assert request.is_completed is True

        db.drop_all()
