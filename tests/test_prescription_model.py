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


def make_app():
    return create_app("testing")


def create_patient(**overrides):
    data = {
        "name_ar": "??? ???",
        "name_en": "Mona Ali",
        "phone_primary": "01011112222",
        "date_of_birth": date(1996, 7, 1),
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return PatientService.create_patient(**data)


def create_visit(patient):
    visit = Visit(
        patient=patient,
        visit_type="gyn",
        visit_date=date(2026, 7, 13),
    )
    db.session.add(visit)
    db.session.commit()
    return visit


def create_drug():
    form = DrugForm(code="tablet", name_en="Tablet")
    route = DrugRoute(code="oral", name_en="Oral")
    db.session.add_all([form, route])
    db.session.commit()

    drug = Drug(
        generic_name="Levofloxacin",
        trade_name="Tavanic",
        strength="500 mg",
        form=form,
        route=route,
    )
    db.session.add(drug)
    db.session.commit()
    return drug, route


def test_prescription_can_be_created_for_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)

        prescription = Prescription(
            patient=patient,
            visit=visit,
            notes="Initial prescription",
        )
        db.session.add(prescription)
        db.session.commit()

        assert prescription.id is not None
        assert prescription.uuid
        assert prescription.visit == visit
        assert prescription.patient == patient
        assert visit.prescription == prescription

        db.drop_all()


def test_prescription_item_can_be_created():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        drug, route = create_drug()

        prescription = Prescription(patient=patient, visit=visit)
        db.session.add(prescription)
        db.session.commit()

        item = PrescriptionItem(
            prescription=prescription,
            drug=drug,
            dose="1 tablet",
            frequency="Every 24 hours",
            duration="5 days",
            instructions_ar="قرص مرة يوميًا لمدة ٥ أيام بعد الأكل",
            route=route,
            sort_order=1,
        )
        db.session.add(item)
        db.session.commit()

        assert item.id is not None
        assert item.uuid
        assert item.prescription == prescription
        assert item.drug == drug
        assert item.route == route
        assert item.instructions_ar == "قرص مرة يوميًا لمدة ٥ أيام بعد الأكل"

        db.drop_all()


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
