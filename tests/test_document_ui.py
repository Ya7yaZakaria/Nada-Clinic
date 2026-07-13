from datetime import date
from io import BytesIO

from werkzeug.datastructures import FileStorage

from app import create_app
from app.extensions import db
from app.models import PatientDocument, User
from app.services.document_service import DocumentService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


def make_app(tmp_path):
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
        PATIENT_DOCUMENT_UPLOAD_FOLDER=str(tmp_path / "uploads" / "patient_documents"),
        PATIENT_DOCUMENT_MAX_FILE_SIZE_BYTES=1024 * 1024,
    )
    return app


def create_user(email, phone, role_name):
    user = User(email=email, phone=phone, name=role_name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)

    return user


def login(client, email):
    return client.post(
        "/auth/login",
        data={
            "login_identifier": email,
            "password": "12345678",
        },
        follow_redirects=True,
    )


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01088880000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def make_file(filename="report.pdf", content=b"fake pdf content", content_type="application/pdf"):
    return FileStorage(
        stream=BytesIO(content),
        filename=filename,
        content_type=content_type,
    )


def test_doctor_can_open_patient_documents_page(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-doc-ui@example.com", "01088880001", "Doctor")
        patient = create_patient()

        client = app.test_client()
        login(client, "doctor-doc-ui@example.com")

        response = client.get(f"/patients/{patient.uuid}/documents")

        assert response.status_code == 200
        assert b"Patient Documents" in response.data
        assert b"No active documents uploaded yet" in response.data

        db.drop_all()


def test_doctor_can_upload_document_and_see_it_in_workspace(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-doc-upload@example.com", "01088880002", "Doctor")
        patient = create_patient(phone_primary="01088880102")

        client = app.test_client()
        login(client, "doctor-doc-upload@example.com")

        response = client.post(
            f"/patients/{patient.uuid}/documents/new",
            data={
                "document_type": PatientDocument.TYPE_INVESTIGATION_REPORT,
                "title": "AMH lab report",
                "description": "Uploaded report",
                "file": (BytesIO(b"fake pdf content"), "amh.pdf"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Document uploaded" in response.data
        assert b"AMH lab report" in response.data

        workspace = client.get(f"/patients/{patient.uuid}")

        assert b"Patient Documents" in workspace.data
        assert b"AMH lab report" in workspace.data
        assert b"amh.pdf" in workspace.data

        document = PatientDocument.query.filter_by(patient_id=patient.id).first()
        assert document is not None

        db.drop_all()


def test_doctor_can_download_document(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-doc-download@example.com", "01088880003", "Doctor")
        patient = create_patient(phone_primary="01088880103")

        document = DocumentService.save_uploaded_file(
            patient=patient,
            file_storage=make_file(content=b"download me"),
            document_type=PatientDocument.TYPE_OTHER,
            title="Download file",
        )

        client = app.test_client()
        login(client, "doctor-doc-download@example.com")

        response = client.get(f"/documents/{document.uuid}/download")

        assert response.status_code == 200
        assert response.data == b"download me"
        assert "attachment" in response.headers.get("Content-Disposition", "")

        db.drop_all()


def test_doctor_can_archive_document(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-doc-archive@example.com", "01088880004", "Doctor")
        patient = create_patient(phone_primary="01088880104")

        document = DocumentService.save_uploaded_file(
            patient=patient,
            file_storage=make_file(),
            document_type=PatientDocument.TYPE_OTHER,
            title="Archive file",
        )

        client = app.test_client()
        login(client, "doctor-doc-archive@example.com")

        response = client.post(
            f"/documents/{document.uuid}/archive",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Document archived" in response.data

        archived = db.session.get(PatientDocument, document.id)
        assert archived.is_active is False

        workspace = client.get(f"/patients/{patient.uuid}")
        assert b"Archive file" not in workspace.data

        db.drop_all()


def test_reception_is_blocked_from_documents(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("reception-doc-ui@example.com", "01088880005", "Reception")
        patient = create_patient(phone_primary="01088880105")

        client = app.test_client()
        login(client, "reception-doc-ui@example.com")

        index_response = client.get(f"/patients/{patient.uuid}/documents")
        upload_response = client.get(f"/patients/{patient.uuid}/documents/new")

        assert index_response.status_code == 403
        assert upload_response.status_code == 403

        db.drop_all()


def test_invalid_file_type_is_rejected(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-doc-invalid@example.com", "01088880006", "Doctor")
        patient = create_patient(phone_primary="01088880106")

        client = app.test_client()
        login(client, "doctor-doc-invalid@example.com")

        response = client.post(
            f"/patients/{patient.uuid}/documents/new",
            data={
                "document_type": PatientDocument.TYPE_OTHER,
                "title": "Invalid",
                "description": "",
                "file": (BytesIO(b"bad"), "malware.exe"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Unsupported file type" in response.data
        assert PatientDocument.query.count() == 0

        db.drop_all()


def test_missing_file_is_rejected(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-doc-missing@example.com", "01088880007", "Doctor")
        patient = create_patient(phone_primary="01088880107")

        client = app.test_client()
        login(client, "doctor-doc-missing@example.com")

        response = client.post(
            f"/patients/{patient.uuid}/documents/new",
            data={
                "document_type": PatientDocument.TYPE_OTHER,
                "title": "Missing",
                "description": "",
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"This field is required" in response.data
        assert PatientDocument.query.count() == 0

        db.drop_all()
