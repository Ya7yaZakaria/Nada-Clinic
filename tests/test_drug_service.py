from app import create_app
from app.extensions import db
from app.models.drug import Drug
from app.models.drug_dictionary import DrugCategory, DrugForm, DrugRoute, DrugSafetyStatus
from app.services.drug_service import DrugService


def make_app():
    return create_app("testing")


def create_dictionary_items():
    category = DrugCategory(code="antibiotic", name_en="Antibiotic")
    form = DrugForm(code="tablet", name_en="Tablet")
    injection_form = DrugForm(code="injection", name_en="Injection")
    route = DrugRoute(code="oral", name_en="Oral")
    pregnancy_status = DrugSafetyStatus(code="caution", name_en="Caution", severity_order=2)
    lactation_status = DrugSafetyStatus(code="safe", name_en="Safe", severity_order=1)

    db.session.add_all([category, form, injection_form, route, pregnancy_status, lactation_status])
    db.session.commit()

    return {
        "category": category,
        "form": form,
        "injection_form": injection_form,
        "route": route,
        "pregnancy_status": pregnancy_status,
        "lactation_status": lactation_status,
    }


def test_create_drug_requires_generic_name():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        try:
            DrugService.create_drug(
                generic_name="",
                trade_name="Tavanic",
                strength="500 mg",
                form=refs["form"],
            )
            assert False
        except ValueError as exc:
            assert "Generic name is required" in str(exc)

        db.drop_all()


def test_create_drug_requires_trade_name():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        try:
            DrugService.create_drug(
                generic_name="Levofloxacin",
                trade_name="",
                strength="500 mg",
                form=refs["form"],
            )
            assert False
        except ValueError as exc:
            assert "Trade name is required" in str(exc)

        db.drop_all()


def test_create_drug_requires_strength():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        try:
            DrugService.create_drug(
                generic_name="Levofloxacin",
                trade_name="Tavanic",
                strength="",
                form=refs["form"],
            )
            assert False
        except ValueError as exc:
            assert "Strength is required" in str(exc)

        db.drop_all()


def test_create_drug_requires_form():
    app = make_app()

    with app.app_context():
        db.create_all()

        try:
            DrugService.create_drug(
                generic_name="Levofloxacin",
                trade_name="Tavanic",
                strength="500 mg",
                form=None,
            )
            assert False
        except ValueError as exc:
            assert "Drug form is required" in str(exc)

        db.drop_all()


def test_create_drug_success():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        drug = DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            category=refs["category"],
            form=refs["form"],
            route=refs["route"],
            pregnancy_status=refs["pregnancy_status"],
            pregnancy_note="Use only after doctor review",
            lactation_status=refs["lactation_status"],
            lactation_note="Doctor note",
            doctor_notes="Common clinic drug",
        )

        assert drug.id
        assert drug.trade_name == "Tavanic"
        assert drug.form.code == "tablet"
        assert drug.pregnancy_status.code == "caution"
        assert drug.lactation_status.code == "safe"

        db.drop_all()


def test_duplicate_trade_form_strength_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            form=refs["form"],
        )

        try:
            DrugService.create_drug(
                generic_name="Levofloxacin",
                trade_name="Tavanic",
                strength="500 mg",
                form=refs["form"],
            )
            assert False
        except ValueError as exc:
            assert "Drug already exists" in str(exc)

        db.drop_all()


def test_same_trade_different_form_is_allowed():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        first = DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            form=refs["form"],
        )
        second = DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            form=refs["injection_form"],
        )

        assert first.id != second.id

        db.drop_all()


def test_same_trade_different_strength_is_allowed():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        first = DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            form=refs["form"],
        )
        second = DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="750 mg",
            form=refs["form"],
        )

        assert first.id != second.id

        db.drop_all()


def test_update_drug_changes_values():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        drug = DrugService.create_drug(
            generic_name="Old Generic",
            trade_name="Old Trade",
            strength="100 mg",
            form=refs["form"],
        )

        DrugService.update_drug(
            drug,
            generic_name="New Generic",
            trade_name="New Trade",
            strength="200 mg",
            form=refs["injection_form"],
            category=refs["category"],
            route=refs["route"],
            pregnancy_status=refs["pregnancy_status"],
            pregnancy_note="Pregnancy note",
            lactation_status=refs["lactation_status"],
            lactation_note="Lactation note",
            doctor_notes="Doctor note",
        )

        assert drug.generic_name == "New Generic"
        assert drug.trade_name == "New Trade"
        assert drug.strength == "200 mg"
        assert drug.form.code == "injection"
        assert drug.category.code == "antibiotic"
        assert drug.route.code == "oral"
        assert drug.pregnancy_status.code == "caution"
        assert drug.lactation_status.code == "safe"

        db.drop_all()


def test_update_duplicate_trade_form_strength_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            form=refs["form"],
        )
        second = DrugService.create_drug(
            generic_name="Other",
            trade_name="Other Brand",
            strength="100 mg",
            form=refs["form"],
        )

        try:
            DrugService.update_drug(
                second,
                trade_name="Tavanic",
                strength="500 mg",
                form=refs["form"],
            )
            assert False
        except ValueError as exc:
            assert "Drug already exists" in str(exc)

        db.drop_all()


def test_inactive_drugs_are_hidden_from_active_list():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        active = DrugService.create_drug(
            generic_name="Active Generic",
            trade_name="Active Brand",
            strength="100 mg",
            form=refs["form"],
        )
        inactive = DrugService.create_drug(
            generic_name="Inactive Generic",
            trade_name="Inactive Brand",
            strength="100 mg",
            form=refs["form"],
        )

        DrugService.deactivate_drug(inactive)

        active_drugs = DrugService.get_active_drugs()

        assert active in active_drugs
        assert inactive not in active_drugs

        db.drop_all()


def test_search_drugs_by_trade_name_generic_name_and_strength():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        DrugService.create_drug(
            generic_name="Levofloxacin",
            trade_name="Tavanic",
            strength="500 mg",
            form=refs["form"],
        )
        DrugService.create_drug(
            generic_name="Paracetamol",
            trade_name="Doliprane",
            strength="1000 mg",
            form=refs["form"],
        )

        assert len(DrugService.search_drugs("Tavanic")) == 1
        assert len(DrugService.search_drugs("Paracetamol")) == 1
        assert len(DrugService.search_drugs("1000")) == 1

        db.drop_all()


def test_empty_search_returns_active_drugs_only():
    app = make_app()

    with app.app_context():
        db.create_all()
        refs = create_dictionary_items()

        active = DrugService.create_drug(
            generic_name="Active Generic",
            trade_name="Active Brand",
            strength="100 mg",
            form=refs["form"],
        )
        inactive = DrugService.create_drug(
            generic_name="Inactive Generic",
            trade_name="Inactive Brand",
            strength="100 mg",
            form=refs["injection_form"],
        )
        DrugService.deactivate_drug(inactive)

        result = DrugService.search_drugs("")

        assert active in result
        assert inactive not in result

        db.drop_all()
