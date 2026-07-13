import hashlib
import mimetypes
import uuid as uuid_lib
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import InvestigationResult, Patient, PatientDocument, Visit


class DocumentService:
    """Backend service for patient document metadata and local file storage."""

    DEFAULT_UPLOAD_SUBDIR = "patient_documents"

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".gif",
        ".txt",
    }

    ALLOWED_MIME_PREFIXES = {
        "image/",
        "text/",
    }

    ALLOWED_MIME_TYPES = {
        "application/pdf",
    }

    DEFAULT_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

    @staticmethod
    def get_storage_root():
        configured = current_app.config.get("PATIENT_DOCUMENT_UPLOAD_FOLDER")

        if configured:
            return Path(configured)

        return Path(current_app.instance_path) / "uploads" / DocumentService.DEFAULT_UPLOAD_SUBDIR

    @staticmethod
    def get_max_file_size():
        return int(
            current_app.config.get(
                "PATIENT_DOCUMENT_MAX_FILE_SIZE_BYTES",
                DocumentService.DEFAULT_MAX_FILE_SIZE_BYTES,
            )
        )

    @staticmethod
    def ensure_storage_root():
        root = DocumentService.get_storage_root()
        root.mkdir(parents=True, exist_ok=True)
        return root

    @staticmethod
    def _get_extension(filename):
        return Path(filename or "").suffix.lower()

    @staticmethod
    def guess_mime_type(filename):
        mime_type, _encoding = mimetypes.guess_type(filename or "")
        return mime_type or "application/octet-stream"

    @staticmethod
    def validate_document_type(document_type):
        document_type = (document_type or PatientDocument.TYPE_OTHER).strip()

        if document_type not in PatientDocument.DOCUMENT_TYPES:
            raise ValueError(f"Invalid document type: {document_type}")

        return document_type

    @staticmethod
    def validate_file(file_storage):
        if not file_storage or not isinstance(file_storage, FileStorage):
            raise ValueError("Document file is required.")

        original_filename = file_storage.filename or ""

        if not original_filename.strip():
            raise ValueError("Document filename is required.")

        extension = DocumentService._get_extension(original_filename)

        if extension not in DocumentService.ALLOWED_EXTENSIONS:
            raise ValueError("Unsupported document file type.")

        stream = file_storage.stream
        current_position = stream.tell()
        stream.seek(0, 2)
        file_size = stream.tell()
        stream.seek(current_position)

        if file_size <= 0:
            raise ValueError("Document file is empty.")

        if file_size > DocumentService.get_max_file_size():
            raise ValueError("Document file is too large.")

        mime_type = file_storage.mimetype or DocumentService.guess_mime_type(original_filename)

        if (
            mime_type not in DocumentService.ALLOWED_MIME_TYPES
            and not any(mime_type.startswith(prefix) for prefix in DocumentService.ALLOWED_MIME_PREFIXES)
        ):
            raise ValueError("Unsupported document MIME type.")

        return {
            "original_filename": original_filename,
            "extension": extension,
            "file_size": file_size,
            "mime_type": mime_type,
        }

    @staticmethod
    def generate_stored_filename(original_filename):
        safe_name = secure_filename(original_filename or "document")
        extension = DocumentService._get_extension(safe_name)

        if not extension:
            extension = DocumentService._get_extension(original_filename)

        token = uuid_lib.uuid4().hex

        if extension:
            return f"{token}{extension}"

        return token

    @staticmethod
    def calculate_checksum(path):
        digest = hashlib.sha256()

        with open(path, "rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def _validate_links(patient, visit=None, investigation_result=None):
        if not patient:
            raise ValueError("Patient is required.")

        if visit and visit.patient_id != patient.id:
            raise ValueError("Visit does not belong to this patient.")

        if investigation_result and investigation_result.patient_id != patient.id:
            raise ValueError("Investigation result does not belong to this patient.")

    @staticmethod
    def save_uploaded_file(
        *,
        patient,
        file_storage,
        document_type=PatientDocument.TYPE_OTHER,
        title=None,
        description=None,
        visit=None,
        investigation_result=None,
        actor_user=None,
    ):
        DocumentService._validate_links(
            patient,
            visit=visit,
            investigation_result=investigation_result,
        )

        document_type = DocumentService.validate_document_type(document_type)
        file_info = DocumentService.validate_file(file_storage)

        storage_root = DocumentService.ensure_storage_root()
        stored_filename = DocumentService.generate_stored_filename(file_info["original_filename"])
        stored_path = storage_root / stored_filename

        file_storage.save(stored_path)

        checksum = DocumentService.calculate_checksum(stored_path)

        document = PatientDocument(
            patient=patient,
            visit=visit,
            investigation_result=investigation_result,
            document_type=document_type,
            title=(title or file_info["original_filename"]).strip(),
            description=(description or "").strip() or None,
            original_filename=file_info["original_filename"],
            stored_filename=stored_filename,
            storage_path=str(stored_path),
            mime_type=file_info["mime_type"],
            file_size=file_info["file_size"],
            checksum=checksum,
            uploaded_by_user=actor_user,
            is_active=True,
        )

        db.session.add(document)
        db.session.commit()

        return document

    @staticmethod
    def create_document_metadata(
        *,
        patient,
        original_filename,
        stored_filename,
        storage_path,
        file_size,
        mime_type=None,
        document_type=PatientDocument.TYPE_OTHER,
        title=None,
        description=None,
        visit=None,
        investigation_result=None,
        actor_user=None,
        checksum=None,
    ):
        DocumentService._validate_links(
            patient,
            visit=visit,
            investigation_result=investigation_result,
        )

        if not original_filename:
            raise ValueError("Original filename is required.")

        if not stored_filename:
            raise ValueError("Stored filename is required.")

        if not storage_path:
            raise ValueError("Storage path is required.")

        if file_size is None or int(file_size) < 0:
            raise ValueError("Valid file size is required.")

        document_type = DocumentService.validate_document_type(document_type)

        document = PatientDocument(
            patient=patient,
            visit=visit,
            investigation_result=investigation_result,
            document_type=document_type,
            title=(title or original_filename).strip(),
            description=(description or "").strip() or None,
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=storage_path,
            mime_type=mime_type or DocumentService.guess_mime_type(original_filename),
            file_size=int(file_size),
            checksum=checksum,
            uploaded_by_user=actor_user,
            is_active=True,
        )

        db.session.add(document)
        db.session.commit()

        return document

    @staticmethod
    def get_document(document_uuid, include_inactive=False):
        query = PatientDocument.query.filter_by(uuid=document_uuid)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.first()

    @staticmethod
    def list_patient_documents(patient, include_inactive=False):
        if not patient:
            raise ValueError("Patient is required.")

        query = PatientDocument.query.filter_by(patient_id=patient.id)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.order_by(PatientDocument.created_at.desc(), PatientDocument.id.desc()).all()

    @staticmethod
    def list_visit_documents(visit, include_inactive=False):
        if not visit:
            raise ValueError("Visit is required.")

        query = PatientDocument.query.filter_by(visit_id=visit.id)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.order_by(PatientDocument.created_at.desc(), PatientDocument.id.desc()).all()

    @staticmethod
    def list_investigation_result_documents(investigation_result, include_inactive=False):
        if not investigation_result:
            raise ValueError("Investigation result is required.")

        query = PatientDocument.query.filter_by(investigation_result_id=investigation_result.id)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.order_by(PatientDocument.created_at.desc(), PatientDocument.id.desc()).all()

    @staticmethod
    def archive_document(document, actor_user=None):
        if not document:
            raise ValueError("Document is required.")

        if not document.is_active:
            return document

        document.is_active = False
        db.session.commit()

        return document

    @staticmethod
    def get_patient(patient_uuid):
        return Patient.query.filter_by(uuid=patient_uuid).first()

    @staticmethod
    def get_visit(visit_uuid):
        return Visit.query.filter_by(uuid=visit_uuid).first()

    @staticmethod
    def get_investigation_result(result_uuid):
        return InvestigationResult.query.filter_by(uuid=result_uuid).first()
