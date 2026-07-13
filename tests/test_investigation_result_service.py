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
    app.config.update(SERVER_NAME="localhost", WTF_CSRF_ENABLED=False)
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
        "phone_primary": "01066630000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient, complaint="Investigation result visit"):
    return VisitService.create_visit(patient=patient, visit_type="gyn", chief_complaint=complaint)


def create_test(code="tsh", name="TSH"):
    category = InvestigationDictionaryService.create_category(code=f"{code}_category", name_en=f"{name} Category")
    return InvestigationDictionaryService.create_test(
        code=code,
        name_en=name,
        category=category,
        default_unit="mIU/L",
        default_reference_range="0.4-4.0",
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def test_result_requires_value_text_or_attachment_reference():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = create_visit(patient)
        test = create_test()
        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        item = InvestigationService.add_order_item(order=order, test=test)

        try:
            InvestigationService.enter_result_for_order_item(order_item=item, result_visit=visit, result_date=date(2026, 7, 13))
        except ValueError as exc:
            assert "result value, text, or attachment" in str(exc)
        else:
            raise AssertionError("Blank result should fail")
        db.drop_all()


def test_order_status_partially_resulted_then_resulted():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient(phone_primary="01066630102")
        visit = create_visit(patient)
        amh = create_test(code="partial_amh", name="AMH")
        tsh = create_test(code="partial_tsh", name="TSH")
        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        amh_item = InvestigationService.add_order_item(order=order, test=amh)
        tsh_item = InvestigationService.add_order_item(order=order, test=tsh)

        InvestigationService.enter_result_for_order_item(order_item=amh_item, result_visit=visit, result_date=date(2026, 7, 13), result_value="1.2")
        db.session.refresh(order)
        assert order.status == InvestigationOrder.STATUS_PARTIALLY_RESULTED

        InvestigationService.enter_result_for_order_item(order_item=tsh_item, result_visit=visit, result_date=date(2026, 7, 13), result_value="2.5")
        db.session.refresh(order)
        assert order.status == InvestigationOrder.STATUS_RESULTED
        db.drop_all()


def test_update_cancel_and_list_result_helpers():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        doctor = create_user("doctor-result-helper@example.com", "01066630103", "Doctor")
        patient = create_patient(phone_primary="01066630103")
        visit = create_visit(patient)
        test = create_test(code="helper_tsh", name="Helper TSH")
        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        item = InvestigationService.add_order_item(order=order, test=test)

        result = InvestigationService.enter_result_for_order_item(
            order_item=item,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            lab_name="Al Borg",
            result_value="4.5",
            abnormal_flag=InvestigationResult.FLAG_HIGH,
            actor_user=doctor,
        )

        InvestigationService.update_result(
            result,
            result_value="2.0",
            abnormal_flag=InvestigationResult.FLAG_NORMAL,
            doctor_comment="Updated",
            actor_user=doctor,
        )

        assert result.result_value == "2.0"
        assert result.abnormal_flag == InvestigationResult.FLAG_NORMAL
        assert result.doctor_comment == "Updated"
        assert InvestigationService.list_results_for_patient(patient) == [result]
        assert InvestigationService.list_results_for_visit(visit) == [result]
        assert InvestigationService.list_results_for_order_item(item) == [result]

        InvestigationService.cancel_result(result)
        db.session.refresh(item)
        db.session.refresh(order)

        assert result.status == InvestigationResult.STATUS_CANCELLED
        assert item.status == InvestigationOrderItem.STATUS_PENDING_RESULT
        assert order.status == InvestigationOrder.STATUS_ORDERED
        assert InvestigationService.list_results_for_patient(patient) == []
        db.drop_all()


def test_historical_result_and_unreviewed_list():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        doctor = create_user("doctor-unreviewed-helper@example.com", "01066630104", "Doctor")
        patient = create_patient(phone_primary="01066630104")
        visit = create_visit(patient)
        amh = create_test(code="unreviewed_amh", name="AMH")
        tsh = create_test(code="unreviewed_tsh", name="TSH")

        reviewed = InvestigationService.enter_historical_result(patient=patient, test=amh, result_visit=visit, result_date=date(2026, 7, 12), result_value="1.0")
        unreviewed = InvestigationService.enter_historical_result(patient=patient, test=tsh, result_visit=visit, result_date=date(2026, 7, 13), result_value="2.0")
        InvestigationService.review_result(reviewed, review_note="Reviewed", actor_user=doctor)

        pending_review = InvestigationService.list_entered_unreviewed_results(patient)

        assert reviewed not in pending_review
        assert unreviewed in pending_review
        db.drop_all()


def test_review_cancelled_result_is_rejected():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient(phone_primary="01066630105")
        visit = create_visit(patient)
        test = create_test(code="review_cancelled", name="Review Cancelled")
        result = InvestigationService.enter_historical_result(patient=patient, test=test, result_visit=visit, result_date=date(2026, 7, 13), result_value="1.0")
        InvestigationService.cancel_result(result)

        try:
            InvestigationService.review_result(result)
        except ValueError as exc:
            assert "Cannot review cancelled" in str(exc)
        else:
            raise AssertionError("Cancelled result review should fail")
        db.drop_all()
