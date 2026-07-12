from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import User
from app.models.drug import Drug
from app.models.drug_dictionary import DrugForm, DrugRoute
from app.models.patient import Patient
from app.services.patient_service import PatientService
from app.services.settings_service import SettingsService
from app.models.prescription import PrescriptionItem
from app.models.visit import Visit
from app.services.prescription_service import PrescriptionService
from app.services.rbac_service import RBACService


def make_app():
    return create_app("testing")


def create_user(email, role_name, phone="01033334444"):
    user = User(email=email, phone=phone, name=role_name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)
    return user


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


def create_drug(active=True):
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
        is_active=active,
    )
    db.session.add(drug)
    db.session.commit()

    return drug, route


def test_create_prescription_for_visit_sets_patient_from_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        doctor = create_user("doctor-prescription@example.com", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)

        prescription = PrescriptionService.create_prescription(
            visit=visit,
            notes="Structured prescription",
            actor_user=doctor,
        )

        assert prescription.id is not None
        assert prescription.patient_id == visit.patient_id
        assert prescription.visit_id == visit.id
        assert prescription.notes == "Structured prescription"
        assert prescription.created_by_user == doctor
        assert prescription.updated_by_user == doctor

        db.drop_all()


def test_duplicate_prescription_for_same_visit_is_rejected():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)

        PrescriptionService.create_prescription(visit=visit)

        with pytest.raises(ValueError, match="Prescription already exists"):
            PrescriptionService.create_prescription(visit=visit)

        db.drop_all()


def test_get_or_create_prescription_returns_existing_prescription():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)

        first = PrescriptionService.get_or_create_prescription(visit=visit)
        second = PrescriptionService.get_or_create_prescription(visit=visit)

        assert first.id == second.id

        db.drop_all()


def test_add_prescription_item_with_drug():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        drug, route = create_drug()
        prescription = PrescriptionService.create_prescription(visit=visit)

        item = PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose="1 tablet",
            frequency="Every 24 hours",
            duration="5 days",
            instructions_ar="قرص مرة يوميًا لمدة ٥ أيام بعد الأكل",
        )

        assert item.id is not None
        assert item.drug == drug
        assert item.route == route
        assert item.dose == "1 tablet"
        assert item.frequency == "Every 24 hours"
        assert item.duration == "5 days"
        assert item.instructions_ar == "قرص مرة يوميًا لمدة ٥ أيام بعد الأكل"

        db.drop_all()


def test_add_item_can_override_route():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        drug, _route = create_drug()
        vaginal_route = DrugRoute(code="vaginal", name_en="Vaginal")
        db.session.add(vaginal_route)
        db.session.commit()

        prescription = PrescriptionService.create_prescription(visit=visit)

        item = PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose="1 tablet",
            frequency="Once daily",
            duration="7 days",
            instructions_ar="قرص مهبلي مرة يوميًا",
            route=vaginal_route,
        )

        assert item.route == vaginal_route

        db.drop_all()


def test_item_required_fields_are_validated():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        drug, _route = create_drug()
        prescription = PrescriptionService.create_prescription(visit=visit)

        with pytest.raises(ValueError, match="Dose is required"):
            PrescriptionService.add_item(
                prescription=prescription,
                drug=drug,
                dose="",
                frequency="Once daily",
                duration="5 days",
                instructions_ar="تعليمات",
            )

        with pytest.raises(ValueError, match="Arabic instructions are required"):
            PrescriptionService.add_item(
                prescription=prescription,
                drug=drug,
                dose="1 tablet",
                frequency="Once daily",
                duration="5 days",
                instructions_ar="",
            )

        db.drop_all()


def test_inactive_drug_cannot_be_prescribed():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        drug, _route = create_drug(active=False)
        prescription = PrescriptionService.create_prescription(visit=visit)

        with pytest.raises(ValueError, match="Inactive drug cannot be prescribed"):
            PrescriptionService.add_item(
                prescription=prescription,
                drug=drug,
                dose="1 tablet",
                frequency="Once daily",
                duration="5 days",
                instructions_ar="تعليمات",
            )

        db.drop_all()


def test_update_prescription_item_changes_values():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        drug, route = create_drug()
        prescription = PrescriptionService.create_prescription(visit=visit)

        item = PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose="1 tablet",
            frequency="Once daily",
            duration="5 days",
            instructions_ar="تعليمات قديمة",
        )

        PrescriptionService.update_item(
            item,
            dose="2 tablets",
            frequency="Every 12 hours",
            duration="7 days",
            instructions_ar="قرصين كل ١٢ ساعة لمدة ٧ أيام",
            route=route,
            sort_order=10,
        )

        assert item.dose == "2 tablets"
        assert item.frequency == "Every 12 hours"
        assert item.duration == "7 days"
        assert item.instructions_ar == "قرصين كل ١٢ ساعة لمدة ٧ أيام"
        assert item.sort_order == 10

        db.drop_all()


def test_remove_prescription_item_deletes_item():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        drug, _route = create_drug()
        prescription = PrescriptionService.create_prescription(visit=visit)

        item = PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose="1 tablet",
            frequency="Once daily",
            duration="5 days",
            instructions_ar="تعليمات",
        )
        item_id = item.id

        PrescriptionService.remove_item(item)

        assert db.session.get(PrescriptionItem, item_id) is None

        db.drop_all()


def test_list_items_orders_by_sort_order():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        drug, _route = create_drug()
        prescription = PrescriptionService.create_prescription(visit=visit)

        second = PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose="2",
            frequency="BID",
            duration="5 days",
            instructions_ar="الثاني",
            sort_order=2,
        )
        first = PrescriptionService.add_item(
            prescription=prescription,
            drug=drug,
            dose="1",
            frequency="OD",
            duration="5 days",
            instructions_ar="الأول",
            sort_order=1,
        )

        items = PrescriptionService.list_items(prescription)

        assert items == [first, second]

        db.drop_all()


def test_doctor_has_prescription_permissions_and_reception_blocked():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        doctor = create_user("doctor-permissions@example.com", "Doctor", phone="01033334444")
        reception = create_user("reception-permissions@example.com", "Reception", phone="01033335555")

        assert RBACService.user_has_permission(doctor, "prescriptions.view")
        assert RBACService.user_has_permission(doctor, "prescriptions.manage")
        assert not RBACService.user_has_permission(reception, "prescriptions.view")
        assert not RBACService.user_has_permission(reception, "prescriptions.manage")

        db.drop_all()
