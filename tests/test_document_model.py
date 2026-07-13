from datetime import date
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import PatientDocument
from app.services.document_service import DocumentService
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_service import InvestigationService
from app.services.patient_service import PatientService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app(tmp_path):
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        PATIENT_DOCUMENT_UPLOAD_FOLDER=str(tmp_path / "uploads" / "patient_documents"),
    )
    return app


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01077770000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def test_patient_document_model_metadata_links_patient_visit_and_result(tmp_path):
    app = make_app(tmp_path)

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient()
        visit = VisitService.create_visit(patient=patient, visit_type="gyn")

        category = InvestigationDictionaryService.create_category(
            code="doc_model_hormonal",
            name_en="Hormonal",
        )
        test = InvestigationDictionaryService.create_test(
            code="doc_model_amh",
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
        )

        document = PatientDocument(
            patient=patient,
            visit=visit,
            investigation_result=result,
            document_type=PatientDocument.TYPE_INVESTIGATION_REPORT,
            title="AMH report",
            original_filename="amh.pdf",
            stored_filename="stored-amh.pdf",
            storage_path=str(Path(app.config["PATIENT_DOCUMENT_UPLOAD_FOLDER"]) / "stored-amh.pdf"),
            mime_type="application/pdf",
            file_size=120,
        )

        db.session.add(document)
        db.session.commit()

        saved = PatientDocument.query.filter_by(uuid=document.uuid).first()

        assert saved is not None
        assert saved.patient_id == patient.id
        assert saved.visit_id == visit.id
        assert saved.investigation_result_id == result.id
        assert saved.document_type == PatientDocument.TYPE_INVESTIGATION_REPORT
        assert saved.is_active is True
        assert saved.is_pdf is True
        assert saved.is_image is False

        db.drop_all()


def test_patient_document_types_are_locked():
    assert PatientDocument.TYPE_INVESTIGATION_REPORT in PatientDocument.DOCUMENT_TYPES
    assert PatientDocument.TYPE_ULTRASOUND_IMAGE in PatientDocument.DOCUMENT_TYPES
    assert PatientDocument.TYPE_OTHER in PatientDocument.DOCUMENT_TYPES
