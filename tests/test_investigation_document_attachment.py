from datetime import date
from io import BytesIO

from app import create_app
from app.extensions import db
from app.models import PatientDocument, User
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
        "phone_primary": "01099990000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_investigation_result(patient):
    visit = VisitService.create_visit(patient=patient, visit_type="gyn")

    category = InvestigationDictionaryService.create_category(
        code="doc_attach_hormonal",
        name_en="Hormonal",
    )
    test = InvestigationDictionaryService.create_test(
        code="doc_attach_amh",
        name_en="AMH",
        category=category,
    )
    order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
    item = InvestigationService.add_order_item(order=order, test=test)

    result = InvestigationService.enter_result_for_order_item(
        order_item=item,
        result_visit=visit,
        result_date=date(2026, 7, 13),
        result_value="2.1",
        lab_name="External Lab",
    )

    return result, order


def test_doctor_can_attach_document_to_investigation_result(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-result-doc@example.com", "01099990001", "Doctor")
        patient = create_patient()
        result, order = create_investigation_result(patient)

        client = app.test_client()
        login(client, "doctor-result-doc@example.com")

        response = client.post(
            f"/investigations/results/{result.uuid}/documents/new",
            data={
                "document_type": PatientDocument.TYPE_INVESTIGATION_REPORT,
                "title": "AMH scanned report",
                "description": "External report scan",
                "file": (BytesIO(b"report pdf"), "amh-report.pdf"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Investigation result document uploaded" in response.data
        assert b"AMH scanned report" in response.data
        assert b"Attached reports" in response.data

        document = PatientDocument.query.filter_by(investigation_result_id=result.id).first()
        assert document is not None
        assert document.patient_id == patient.id
        assert document.visit_id == result.result_visit_id
        assert document.document_type == PatientDocument.TYPE_INVESTIGATION_REPORT

        db.session.refresh(result)
        assert result.has_attachment is True
        assert result.attachment_label == "AMH scanned report"
        assert result.external_report_reference == "amh-report.pdf"

        db.drop_all()


def test_attached_document_appears_on_patient_investigations_page(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-result-doc-list@example.com", "01099990002", "Doctor")
        patient = create_patient(phone_primary="01099990102")
        result, order = create_investigation_result(patient)

        client = app.test_client()
        login(client, "doctor-result-doc-list@example.com")

        client.post(
            f"/investigations/results/{result.uuid}/documents/new",
            data={
                "document_type": PatientDocument.TYPE_INVESTIGATION_REPORT,
                "title": "AMH result PDF",
                "description": "",
                "file": (BytesIO(b"report pdf"), "amh-result.pdf"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        response = client.get(f"/investigations/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"AMH result PDF" in response.data
        assert b"Reports:" in response.data

        db.drop_all()


def test_reception_is_blocked_from_attaching_investigation_document(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("reception-result-doc@example.com", "01099990003", "Reception")
        patient = create_patient(phone_primary="01099990103")
        result, order = create_investigation_result(patient)

        client = app.test_client()
        login(client, "reception-result-doc@example.com")

        response = client.get(f"/investigations/results/{result.uuid}/documents/new")

        assert response.status_code == 403

        db.drop_all()


def test_invalid_investigation_result_document_file_is_rejected(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-result-doc-invalid@example.com", "01099990004", "Doctor")
        patient = create_patient(phone_primary="01099990104")
        result, order = create_investigation_result(patient)

        client = app.test_client()
        login(client, "doctor-result-doc-invalid@example.com")

        response = client.post(
            f"/investigations/results/{result.uuid}/documents/new",
            data={
                "document_type": PatientDocument.TYPE_INVESTIGATION_REPORT,
                "title": "Bad file",
                "description": "",
                "file": (BytesIO(b"bad"), "bad.exe"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Unsupported file type" in response.data
        assert PatientDocument.query.count() == 0

        db.drop_all()
