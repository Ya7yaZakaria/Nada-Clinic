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
        "phone_primary": "01066830000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Investigation review visit",
    )


def create_test(code="review_tsh", name="Review TSH"):
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


def test_review_result_updates_result_item_and_order_status():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-review-service@example.com", "01066830001", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)
        test = create_test()

        order = InvestigationService.create_order(patient=patient, ordered_visit=visit)
        item = InvestigationService.add_order_item(order=order, test=test)
        result = InvestigationService.enter_result_for_order_item(
            order_item=item,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="2.1",
            abnormal_flag=InvestigationResult.FLAG_UNKNOWN,
        )

        reviewed = InvestigationService.review_result(
            result,
            review_note="Reviewed and accepted",
            abnormal_flag=InvestigationResult.FLAG_NORMAL,
            actor_user=doctor,
        )

        db.session.refresh(item)
        db.session.refresh(order)

        assert reviewed.status == InvestigationResult.STATUS_REVIEWED
        assert reviewed.review_note == "Reviewed and accepted"
        assert reviewed.reviewed_by_user == doctor
        assert reviewed.reviewed_at is not None
        assert reviewed.abnormal_flag == InvestigationResult.FLAG_NORMAL
        assert item.status == InvestigationOrderItem.STATUS_REVIEWED
        assert order.status == InvestigationOrder.STATUS_REVIEWED

        db.drop_all()


def test_pending_results_excludes_reviewed_results():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-pending-review-service@example.com", "01066830002", "Doctor")
        patient = create_patient(phone_primary="01066830102")
        visit = create_visit(patient)
        reviewed_test = create_test(code="reviewed_result", name="Reviewed Result")
        pending_test = create_test(code="pending_result", name="Pending Result")

        reviewed_result = InvestigationService.enter_historical_result(
            patient=patient,
            test=reviewed_test,
            result_visit=visit,
            result_date=date(2026, 7, 12),
            result_value="1.0",
        )
        pending_result = InvestigationService.enter_historical_result(
            patient=patient,
            test=pending_test,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="2.0",
        )

        InvestigationService.review_result(reviewed_result, actor_user=doctor)

        pending = InvestigationService.list_patient_pending_results(patient)

        assert reviewed_result not in pending
        assert pending_result in pending

        db.drop_all()


def test_review_cancelled_result_is_blocked():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01066830103")
        visit = create_visit(patient)
        test = create_test(code="cancelled_review", name="Cancelled Review")

        result = InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            result_value="1.0",
        )
        InvestigationService.cancel_result(result)

        try:
            InvestigationService.review_result(result)
        except ValueError as exc:
            assert "Cannot review cancelled" in str(exc)
        else:
            raise AssertionError("Cancelled result review should fail")

        db.drop_all()
