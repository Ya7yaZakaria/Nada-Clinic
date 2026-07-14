from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import ExternalUltrasoundRequest, PatientDocument, User
from app.services.document_service import DocumentService
from app.services.external_ultrasound_service import ExternalUltrasoundService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_patient(phone="01088880300"):
    return PatientService.create_patient(
        name_ar="منى علي",
        name_en="Mona Ali",
        phone_primary=phone,
        date_of_birth=date(1996, 7, 1),
    )


def create_user(email, phone, role_name):
    user = User(email=email, phone=phone, name=role_name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)

    return user


def create_document(patient, visit, filename="external-us.pdf"):
    return DocumentService.create_document_metadata(
        patient=patient,
        visit=visit,
        original_filename=filename,
        stored_filename=filename,
        storage_path=f"/tmp/{filename}",
        file_size=10,
        mime_type="application/pdf",
        document_type=PatientDocument.TYPE_ULTRASOUND_REPORT,
        title="External ultrasound report",
        description="External ultrasound notes",
    )


def test_create_external_request_from_visit_uses_only_request_note():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-external-us@example.com", "01088880301", "Doctor")
        patient = create_patient()
        visit = VisitService.create_visit(patient=patient, visit_type="obs")

        request = ExternalUltrasoundService.create_request(
            visit=visit,
            request_note="Growth scan + Doppler outside.",
            actor_user=doctor,
        )

        assert request.id is not None
        assert request.patient_id == patient.id
        assert request.requested_visit_id == visit.id
        assert request.created_by_user_id == doctor.id
        assert request.status == ExternalUltrasoundRequest.STATUS_PENDING
        assert request.request_note == "Growth scan + Doppler outside."

        db.drop_all()


def test_create_external_request_rejects_empty_note():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone="01088880302")
        visit = VisitService.create_visit(patient=patient, visit_type="obs")

        with pytest.raises(ValueError, match="External ultrasound request note is required"):
            ExternalUltrasoundService.create_request(
                visit=visit,
                request_note="",
            )

        db.drop_all()


def test_list_pending_and_cancel_external_request():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone="01088880303")
        visit = VisitService.create_visit(patient=patient, visit_type="gyn")

        request = ExternalUltrasoundService.create_request(
            visit=visit,
            request_note="Pelvic ultrasound outside.",
        )

        assert request in ExternalUltrasoundService.list_pending_for_patient(patient)

        ExternalUltrasoundService.cancel_request(request)

        assert request.status == ExternalUltrasoundRequest.STATUS_CANCELLED
        assert request not in ExternalUltrasoundService.list_pending_for_patient(patient)

        db.drop_all()


def test_complete_external_request_with_document():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-complete-us@example.com", "01088880304", "Doctor")
        patient = create_patient(phone="01088880305")
        request_visit = VisitService.create_visit(patient=patient, visit_type="obs")
        result_visit = VisitService.create_visit(patient=patient, visit_type="obs")
        document = create_document(patient, result_visit)

        request = ExternalUltrasoundService.create_request(
            visit=request_visit,
            request_note="Growth scan outside.",
        )

        completed = ExternalUltrasoundService.complete_request_with_document(
            request=request,
            result_visit=result_visit,
            result_document=document,
            actor_user=doctor,
        )

        assert completed.status == ExternalUltrasoundRequest.STATUS_COMPLETED
        assert completed.result_visit_id == result_visit.id
        assert completed.result_document_id == document.id
        assert completed.completed_by_user_id == doctor.id
        assert completed.completed_at is not None

        db.drop_all()


def test_complete_external_request_rejects_wrong_patient_links():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone="01088880306")
        other_patient = create_patient(phone="01088880307")

        request_visit = VisitService.create_visit(patient=patient, visit_type="obs")
        other_visit = VisitService.create_visit(patient=other_patient, visit_type="obs")
        other_document = create_document(other_patient, other_visit, filename="other-us.pdf")

        request = ExternalUltrasoundService.create_request(
            visit=request_visit,
            request_note="Growth scan outside.",
        )

        with pytest.raises(ValueError, match="Result visit does not belong to request patient"):
            ExternalUltrasoundService.complete_request_with_document(
                request=request,
                result_visit=other_visit,
                result_document=other_document,
            )

        db.drop_all()
