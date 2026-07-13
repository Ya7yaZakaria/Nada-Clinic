from datetime import date

from app import create_app
from app.extensions import db
from app.models import User
from app.models.investigation import InvestigationOrder, InvestigationOrderItem, InvestigationResult, InvestigationTest
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_service import InvestigationService
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


def create_user(email, phone, role_name, name="Test User"):
    user = User(email=email, phone=phone, name=name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)
    return user


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01066220000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Investigation visit",
    )


def create_test(code="tsh", name="TSH"):
    category = InvestigationDictionaryService.create_category(
        code=f"{code}_category",
        name_en=f"{name} Category",
    )
    return InvestigationDictionaryService.create_test(
        code=code,
        name_en=name,
        category=category,
        default_unit="mIU/L",
        default_reference_range="0.4-4.0",
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def test_create_order_and_add_order_item():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-investigation-order@example.com", "01066220001", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        test = create_test()

        order = InvestigationService.create_order(
            patient=patient,
            ordered_visit=visit,
            priority=InvestigationOrder.PRIORITY_IMPORTANT,
            actor_user=doctor,
        )
        item = InvestigationService.add_order_item(order=order, test=test)

        assert order.patient == patient
        assert order.ordered_visit == visit
        assert order.ordered_by_user == doctor
        assert item.order == order
        assert item.test == test
        assert item.status == InvestigationOrderItem.STATUS_PENDING_RESULT

        db.drop_all()


def test_enter_result_for_order_item_updates_statuses():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-investigation-result@example.com", "01066220002", "Doctor")
        patient = create_patient(phone_primary="01066220102")
        ordered_visit = create_visit(patient)
        result_visit = create_visit(patient)
        test = create_test()

        order = InvestigationService.create_order(
            patient=patient,
            ordered_visit=ordered_visit,
            actor_user=doctor,
        )
        item = InvestigationService.add_order_item(order=order, test=test)

        result = InvestigationService.enter_result_for_order_item(
            order_item=item,
            result_visit=result_visit,
            result_date=date(2026, 7, 13),
            lab_name="Al Borg",
            result_value="2.1",
            abnormal_flag=InvestigationResult.FLAG_NORMAL,
            doctor_comment="Acceptable result",
            actor_user=doctor,
        )

        db.session.refresh(item)
        db.session.refresh(order)

        assert result.order_item == item
        assert result.ordered_visit == ordered_visit
        assert result.result_visit == result_visit
        assert result.entered_by_user == doctor
        assert result.lab_name == "Al Borg"
        assert item.status == InvestigationOrderItem.STATUS_RESULT_ENTERED
        assert order.status == InvestigationOrder.STATUS_RESULTED

        db.drop_all()


def test_enter_historical_result_without_prior_order():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-historical-result@example.com", "01066220003", "Doctor")
        patient = create_patient(phone_primary="01066220103")
        visit = create_visit(patient)
        test = create_test(code="amh", name="AMH")

        result = InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 10),
            lab_name="Al Mokhtabar",
            result_value="1.2",
            unit="ng/mL",
            doctor_comment="Old external result",
            actor_user=doctor,
        )

        assert result.order_item is None
        assert result.result_visit == visit
        assert result.ordered_visit is None
        assert result.entered_by_user == doctor

        db.drop_all()


def test_latest_result_returns_newest_result_for_test():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01066220104")
        visit = create_visit(patient)
        test = create_test(code="tsh_latest", name="TSH Latest")

        old_result = InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 1),
            result_value="4.0",
        )
        new_result = InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="2.0",
        )

        latest = InvestigationService.get_latest_result(patient, test)

        assert latest == new_result
        assert latest != old_result

        db.drop_all()


def test_pending_order_items_excludes_result_entered_items():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01066220105")
        visit = create_visit(patient)
        test_pending = create_test(code="pending_tsh", name="Pending TSH")
        test_resulted = create_test(code="resulted_amh", name="Resulted AMH")

        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        pending_item = InvestigationService.add_order_item(order=order, test=test_pending)
        resulted_item = InvestigationService.add_order_item(order=order, test=test_resulted)

        InvestigationService.enter_result_for_order_item(
            order_item=resulted_item,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="1.2",
        )

        pending_items = InvestigationService.list_pending_order_items(patient)

        assert pending_item in pending_items
        assert resulted_item not in pending_items

        db.drop_all()


def test_find_missing_tests_uses_latest_results():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01066220106")
        visit = create_visit(patient)
        amh = create_test(code="missing_amh", name="AMH")
        tsh = create_test(code="missing_tsh", name="TSH")
        prolactin = create_test(code="missing_prl", name="Prolactin")

        InvestigationService.enter_historical_result(
            patient=patient,
            test=amh,
            result_visit=visit,
            result_date=date(2026, 7, 10),
            result_value="1.2",
        )

        missing = InvestigationService.find_missing_tests(patient, [amh, tsh, prolactin])

        assert amh not in missing
        assert tsh in missing
        assert prolactin in missing

        db.drop_all()


def test_reception_does_not_receive_investigation_permissions():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-investigation-rbac@example.com", "01066220007", "Doctor")
        reception = create_user("reception-investigation-rbac@example.com", "01066220008", "Reception")

        assert RBACService.user_has_permission(doctor, "investigations.view")
        assert RBACService.user_has_permission(doctor, "investigations.manage")
        assert RBACService.user_has_permission(doctor, "investigation_results.review")
        assert not RBACService.user_has_permission(reception, "investigations.view")
        assert not RBACService.user_has_permission(reception, "investigations.manage")
        assert not RBACService.user_has_permission(reception, "investigation_results.review")

        db.drop_all()
