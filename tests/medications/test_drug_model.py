from tests.factories import create_drug_dictionary_items as create_dictionary_items
from tests.factories import make_app

from app import create_app
from app.extensions import db
from app.models.drug import Drug
from app.models.drug_dictionary import DrugCategory, DrugForm, DrugRoute, DrugSafetyStatus
from app.services.drug_service import DrugService


def test_drug_model_stores_required_fields_and_relationships():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        drug = Drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            category=refs["category"],
            form=refs["form"],
            route=refs["route"],
            pregnancy_status=refs["pregnancy_status"],
            pregnancy_note="Doctor review required",
            lactation_status=refs["lactation_status"],
            lactation_note="Doctor note",
            doctor_notes="Clinic preferred brand",
        )

        db.session.add(drug)
        db.session.commit()

        assert drug.uuid
        assert drug.generic_name == "Levofloxacin"
        assert drug.trade_name == "Tavanic"
        assert drug.strength == "500 mg"
        assert drug.category.code == "antibiotic"
        assert drug.form.code == "tablet"
        assert drug.route.code == "oral"
        assert drug.pregnancy_status.code == "caution"
        assert drug.lactation_status.code == "safe"
        assert drug.is_active is True

        db.drop_all()


