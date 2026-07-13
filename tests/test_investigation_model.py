from datetime import date

from app import create_app
from app.extensions import db
from app.models.investigation import (
    InvestigationCategory,
    InvestigationOrder,
    InvestigationOrderItem,
    InvestigationResult,
    InvestigationTest,
)
from app.services.investigation_dictionary_service import InvestigationDictionaryService
from app.services.investigation_service import InvestigationService
from app.services.patient_service import PatientService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
    )
    return app


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01066110000",
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


def test_investigation_core_models_can_be_created():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient()
        visit = create_visit(patient)

        category = InvestigationCategory(
            code="hormonal",
            name_en="Hormonal",
            name_ar="هرمونات",
        )
        test = InvestigationTest(
            code="tsh",
            name_en="TSH",
            category=category,
            default_unit="mIU/L",
            result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
        )
        order = InvestigationOrder(
            patient=patient,
            ordered_visit=visit,
            priority=InvestigationOrder.PRIORITY_ROUTINE,
        )
        item = InvestigationOrderItem(
            order=order,
            test=test,
            status=InvestigationOrderItem.STATUS_PENDING_RESULT,
            sort_order=1,
        )
        result = InvestigationResult(
            patient=patient,
            test=test,
            order_item=item,
            ordered_visit=visit,
            result_visit=visit,
            result_date=date(2026, 7, 13),
            lab_name="Al Borg",
            result_value="2.1",
            unit="mIU/L",
            abnormal_flag=InvestigationResult.FLAG_NORMAL,
            status=InvestigationResult.STATUS_ENTERED,
        )

        db.session.add_all([category, test, order, item, result])
        db.session.commit()

        assert category.id is not None
        assert test.category == category
        assert order.patient == patient
        assert order.ordered_visit == visit
        assert item.order == order
        assert item.test == test
        assert result.order_item == item
        assert result.result_visit == visit

        db.drop_all()


def test_historical_result_can_exist_without_order_item():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone_primary="01066110001")
        visit = create_visit(patient)
        category = InvestigationDictionaryService.create_category(
            code="hormonal",
            name_en="Hormonal",
        )
        test = InvestigationDictionaryService.create_test(
            code="amh",
            name_en="AMH",
            category=category,
            default_unit="ng/mL",
            result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
        )

        result = InvestigationService.enter_historical_result(
            patient=patient,
            test=test,
            result_visit=visit,
            result_date=date(2026, 7, 10),
            lab_name="Al Mokhtabar",
            result_value="1.2",
            abnormal_flag=InvestigationResult.FLAG_NORMAL,
        )

        assert result.order_item is None
        assert result.ordered_visit is None
        assert result.result_visit == visit
        assert result.patient == patient

        db.drop_all()
