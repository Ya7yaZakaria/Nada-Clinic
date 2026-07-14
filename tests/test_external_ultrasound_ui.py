from datetime import date
from io import BytesIO

from app import create_app
from app.extensions import db
from app.models import ExternalUltrasoundRequest, PatientDocument, User
from app.services.external_ultrasound_service import ExternalUltrasoundService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
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


def create_patient(phone="01088880500"):
    return PatientService.create_patient(
        name_ar="منى علي",
        name_en="Mona Ali",
        phone_primary=phone,
        date_of_birth=date(1996, 7, 1),
    )


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="obs",
        chief_complaint="Routine visit",
        plan="Plan remains outside ultrasound.",
    )


def setup_doctor_context(email="doctor-external-us@example.com", phone="01088880501"):
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user(email, phone, "Doctor")
        patient = create_patient()
        visit = create_visit(patient)

        yield app, doctor, patient, visit

        db.drop_all()


def test_doctor_can_create_external_us_request_from_visit():
    for app, doctor, patient, visit in setup_doctor_context(
        "doctor-external-request@example.com",
        "01088880511",
    ):
        client = app.test_client()
        login(client, "doctor-external-request@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/external-ultrasounds/requests",
            data={
                "categories": ["obs"],
                "modalities": ["2d", "doppler"],
                "request_note": "Growth scan with Doppler.",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"External ultrasound request saved" in response.data
        assert b"Growth scan with Doppler" in response.data

        request_record = ExternalUltrasoundRequest.query.filter_by(patient_id=patient.id).first()
        assert request_record is not None
        assert request_record.status == ExternalUltrasoundRequest.STATUS_PENDING
        assert request_record.request_categories_json == ["obs"]
        assert request_record.request_modalities_json == ["2d", "doppler"]


def test_doctor_can_add_direct_note_only_external_us_result():
    for app, doctor, patient, visit in setup_doctor_context(
        "doctor-external-note@example.com",
        "01088880512",
    ):
        client = app.test_client()
        login(client, "doctor-external-note@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/external-ultrasounds/results",
            data={
                "document_type": PatientDocument.TYPE_ULTRASOUND_REPORT,
                "request_uuid": "",
                "categories": ["gyne"],
                "modalities": ["tvs"],
                "title": "",
                "result_note": "External US reviewed from patient phone: normal adnexa.",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"External ultrasound result saved" in response.data
        assert b"normal adnexa" in response.data

        result = ExternalUltrasoundRequest.query.filter_by(patient_id=patient.id).first()
        assert result.status == ExternalUltrasoundRequest.STATUS_COMPLETED
        assert result.result_document is None
        assert result.result_note == "External US reviewed from patient phone: normal adnexa."
        assert result.result_visit_id == visit.id


def test_doctor_can_add_direct_file_external_us_result_with_thumbnail():
    for app, doctor, patient, visit in setup_doctor_context(
        "doctor-external-file@example.com",
        "01088880513",
    ):
        client = app.test_client()
        login(client, "doctor-external-file@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/external-ultrasounds/results",
            data={
                "document_type": PatientDocument.TYPE_ULTRASOUND_IMAGE,
                "request_uuid": "",
                "categories": ["obs"],
                "modalities": ["2d"],
                "title": "External fetal US image",
                "result_note": "Reviewed image.",
                "file": (BytesIO(b"fake image bytes"), "external_us.jpg"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"External ultrasound result saved" in response.data
        assert b"External fetal US image" in response.data
        assert b"img-thumbnail" in response.data

        document = PatientDocument.query.filter_by(patient_id=patient.id).first()
        assert document is not None
        assert document.document_type == PatientDocument.TYPE_ULTRASOUND_IMAGE
        assert document.visit_id == visit.id

        result = ExternalUltrasoundRequest.query.filter_by(patient_id=patient.id).first()
        assert result.status == ExternalUltrasoundRequest.STATUS_COMPLETED
        assert result.result_document_id == document.id


def test_doctor_can_complete_pending_request_with_note_only():
    for app, doctor, patient, visit in setup_doctor_context(
        "doctor-external-complete-note@example.com",
        "01088880514",
    ):
        pending = ExternalUltrasoundService.create_request(
            visit=visit,
            request_note="Pelvic ultrasound for endometrium.",
            categories=["gyne"],
            modalities=["tvs"],
            actor_user=doctor,
        )

        client = app.test_client()
        login(client, "doctor-external-complete-note@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/external-ultrasounds/requests/{pending.uuid}/result",
            data={
                "document_type": PatientDocument.TYPE_ULTRASOUND_REPORT,
                "title": "",
                "result_note": "External report reviewed: ET 8 mm.",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"External ultrasound request completed" in response.data
        assert b"ET 8 mm" in response.data

        updated = db.session.get(ExternalUltrasoundRequest, pending.id)
        assert updated.status == ExternalUltrasoundRequest.STATUS_COMPLETED
        assert updated.result_document_id is None
        assert updated.result_note == "External report reviewed: ET 8 mm."


def test_doctor_can_complete_pending_request_with_file():
    for app, doctor, patient, visit in setup_doctor_context(
        "doctor-external-complete-file@example.com",
        "01088880515",
    ):
        pending = ExternalUltrasoundService.create_request(
            visit=visit,
            request_note="Growth scan.",
            categories=["obs"],
            modalities=["2d"],
            actor_user=doctor,
        )

        client = app.test_client()
        login(client, "doctor-external-complete-file@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/external-ultrasounds/requests/{pending.uuid}/result",
            data={
                "document_type": PatientDocument.TYPE_ULTRASOUND_REPORT,
                "title": "External growth scan",
                "result_note": "Growth scan reviewed.",
                "file": (BytesIO(b"%PDF fake"), "growth_scan.pdf"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"External ultrasound request completed" in response.data
        assert b"External growth scan" in response.data

        updated = db.session.get(ExternalUltrasoundRequest, pending.id)
        assert updated.status == ExternalUltrasoundRequest.STATUS_COMPLETED
        assert updated.result_document_id is not None
        assert updated.result_note == "Growth scan reviewed."


def test_empty_external_us_result_is_rejected():
    for app, doctor, patient, visit in setup_doctor_context(
        "doctor-external-empty@example.com",
        "01088880516",
    ):
        client = app.test_client()
        login(client, "doctor-external-empty@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/external-ultrasounds/results",
            data={
                "document_type": PatientDocument.TYPE_ULTRASOUND_REPORT,
                "request_uuid": "",
                "title": "",
                "result_note": "",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Add a file or write a doctor review note" in response.data
        assert ExternalUltrasoundRequest.query.count() == 0


def test_reception_is_blocked_from_external_us_routes():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-external-owner@example.com", "01088880517", "Doctor")
        create_user("reception-external-blocked@example.com", "01088880518", "Reception")

        patient = create_patient()
        visit = create_visit(patient)

        pending = ExternalUltrasoundService.create_request(
            visit=visit,
            request_note="External US request.",
            actor_user=doctor,
        )

        client = app.test_client()
        login(client, "reception-external-blocked@example.com")

        request_response = client.post(
            f"/visits/{visit.uuid}/external-ultrasounds/requests",
            data={"request_note": "Blocked request"},
        )
        result_response = client.post(
            f"/visits/{visit.uuid}/external-ultrasounds/results",
            data={"result_note": "Blocked result"},
        )
        complete_response = client.post(
            f"/visits/{visit.uuid}/external-ultrasounds/requests/{pending.uuid}/result",
            data={"result_note": "Blocked completion"},
        )
        cancel_response = client.post(
            f"/external-ultrasounds/requests/{pending.uuid}/cancel",
        )

        assert request_response.status_code == 403
        assert result_response.status_code == 403
        assert complete_response.status_code == 403
        assert cancel_response.status_code == 403

        db.drop_all()
