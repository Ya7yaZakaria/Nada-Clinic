from datetime import date
from io import BytesIO
from pathlib import Path

import pytest
from werkzeug.datastructures import FileStorage

from app import create_app
from app.extensions import db
from app.models import PatientDocument, Permission, User
from app.services.document_service import DocumentService
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_service import InvestigationService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app(tmp_path):
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        PATIENT_DOCUMENT_UPLOAD_FOLDER=str(tmp_path / "uploads" / "patient_documents"),
        PATIENT_DOCUMENT_MAX_FILE_SIZE_BYTES=1024 * 1024,
    )
    return app


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01077770100",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_user(email, phone, role_name):
    user = User(email=email, phone=phone, name=role_name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)

    return user


def make_file(filename="report.pdf", content=b"fake pdf content", content_type="application/pdf"):
    return FileStorage(
        stream=BytesIO(content),
        filename=filename,
        content_type=content_type,
    )


def create_result(patient, visit):
    category = InvestigationDictionaryService.create_category(
        code="doc_service_hormonal",
        name_en="Hormonal",
    )
    test = InvestigationDictionaryService.create_test(
        code="doc_service_amh",
        name_en="AMH",
        category=category,
    )
    order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
    item = InvestigationService.add_order_item(order=order, test=test)

    return InvestigationService.enter_result_for_order_item(
        order_item=item,
        result_visit=visit,
        result_date=date(2026, 7, 13),
        result_value="2.1",
    )


def test_save_uploaded_file_creates_file_and_metadata(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-documents@example.com", "01077770101", "Doctor")
        patient = create_patient()
        visit = VisitService.create_visit(patient=patient, visit_type="gyn")
        result = create_result(patient, visit)

        document = DocumentService.save_uploaded_file(
            patient=patient,
            visit=visit,
            investigation_result=result,
            file_storage=make_file(),
            document_type=PatientDocument.TYPE_INVESTIGATION_REPORT,
            title="AMH report",
            description="External lab report",
            actor_user=doctor,
        )

        stored_path = Path(document.storage_path)

        assert document.id is not None
        assert document.patient_id == patient.id
        assert document.visit_id == visit.id
        assert document.investigation_result_id == result.id
        assert document.uploaded_by_user_id == doctor.id
        assert document.document_type == PatientDocument.TYPE_INVESTIGATION_REPORT
        assert document.original_filename == "report.pdf"
        assert document.stored_filename.endswith(".pdf")
        assert stored_path.exists()
        assert stored_path.read_bytes() == b"fake pdf content"
        assert document.file_size == len(b"fake pdf content")
        assert document.checksum is not None

        db.drop_all()


def test_list_patient_documents_excludes_archived(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient()

        active_document = DocumentService.create_document_metadata(
            patient=patient,
            original_filename="active.pdf",
            stored_filename="active.pdf",
            storage_path="/tmp/active.pdf",
            file_size=10,
            document_type=PatientDocument.TYPE_OTHER,
        )

        archived_document = DocumentService.create_document_metadata(
            patient=patient,
            original_filename="archived.pdf",
            stored_filename="archived.pdf",
            storage_path="/tmp/archived.pdf",
            file_size=10,
            document_type=PatientDocument.TYPE_OTHER,
        )
        DocumentService.archive_document(archived_document)

        active_documents = DocumentService.list_patient_documents(patient)
        all_documents = DocumentService.list_patient_documents(patient, include_inactive=True)

        assert active_document in active_documents
        assert archived_document not in active_documents
        assert active_document in all_documents
        assert archived_document in all_documents

        db.drop_all()


def test_rejects_unsupported_extension(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient()

        with pytest.raises(ValueError, match="Unsupported document file type"):
            DocumentService.save_uploaded_file(
                patient=patient,
                file_storage=make_file(filename="malware.exe", content_type="application/octet-stream"),
            )

        db.drop_all()


def test_rejects_missing_patient(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        with pytest.raises(ValueError, match="Patient is required"):
            DocumentService.save_uploaded_file(
                patient=None,
                file_storage=make_file(),
            )

        db.drop_all()


def test_rejects_wrong_visit_patient(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01077770105")
        other_patient = create_patient(phone_primary="01077770106")
        other_visit = VisitService.create_visit(patient=other_patient, visit_type="gyn")

        with pytest.raises(ValueError, match="Visit does not belong to this patient"):
            DocumentService.save_uploaded_file(
                patient=patient,
                visit=other_visit,
                file_storage=make_file(),
            )

        db.drop_all()


def test_rejects_wrong_investigation_result_patient(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01077770107")
        other_patient = create_patient(phone_primary="01077770108")
        other_visit = VisitService.create_visit(patient=other_patient, visit_type="gyn")
        other_result = create_result(other_patient, other_visit)

        with pytest.raises(ValueError, match="Investigation result does not belong to this patient"):
            DocumentService.save_uploaded_file(
                patient=patient,
                investigation_result=other_result,
                file_storage=make_file(),
            )

        db.drop_all()


def test_seed_document_permissions_for_admin_doctor_only(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        RBACService.seed_roles_permissions()

        assert Permission.query.filter_by(name="documents.view").first() is not None
        assert Permission.query.filter_by(name="documents.manage").first() is not None

        admin = create_user("admin-documents@example.com", "01077770109", "Admin")
        doctor = create_user("doctor-documents-rbac@example.com", "01077770110", "Doctor")
        reception = create_user("reception-documents@example.com", "01077770111", "Reception")

        assert RBACService.user_has_permission(admin, "documents.view")
        assert RBACService.user_has_permission(admin, "documents.manage")
        assert RBACService.user_has_permission(doctor, "documents.view")
        assert RBACService.user_has_permission(doctor, "documents.manage")
        assert not RBACService.user_has_permission(reception, "documents.view")
        assert not RBACService.user_has_permission(reception, "documents.manage")

        db.drop_all()
