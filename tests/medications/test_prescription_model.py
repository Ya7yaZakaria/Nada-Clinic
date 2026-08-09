from tests.factories import create_basic_drug as create_drug
from tests.factories import create_prescription_patient as create_patient
from tests.factories import create_prescription_visit as create_visit
from tests.factories import make_app

from datetime import date

from app import create_app
from app.extensions import db
from app.models.drug import Drug
from app.models.drug_dictionary import DrugForm, DrugRoute
from app.models.patient import Patient
from app.services.patient_service import PatientService
from app.services.settings_service import SettingsService
from app.models.prescription import Prescription, PrescriptionItem
from app.models.visit import Visit


def test_one_prescription_per_visit_database_constraint():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)

        first = Prescription(patient_id=patient.id, visit_id=visit.id)
        db.session.add(first)
        db.session.commit()

        second = Prescription(patient_id=patient.id, visit_id=visit.id)
        db.session.add(second)

        try:
            db.session.commit()
            assert False, "Expected unique constraint failure"
        except Exception:
            db.session.rollback()

        db.drop_all()
