from datetime import datetime, timezone

from app.extensions import db
from app.models.investigation import (
    InvestigationOrder,
    InvestigationOrderItem,
    InvestigationResult,
    InvestigationTest,
)
from app.models.journey import Journey
from app.models.patient import Patient
from app.models.visit import Visit


class InvestigationService:
    """Service layer for investigation orders, results, latest results, and pending logic."""

    @staticmethod
    def _clean(value):
        return (value or "").strip()

    @classmethod
    def _require_text(cls, value, message):
        cleaned = cls._clean(value)
        if not cleaned:
            raise ValueError(message)
        return cleaned

    @staticmethod
    def _validate_patient(patient):
        if not patient:
            raise ValueError("Patient is required")
        if not isinstance(patient, Patient):
            raise ValueError("Invalid patient")

    @staticmethod
    def _validate_visit(visit):
        if visit is not None and not isinstance(visit, Visit):
            raise ValueError("Invalid visit")

    @staticmethod
    def _validate_journey(journey):
        if journey is not None and not isinstance(journey, Journey):
            raise ValueError("Invalid journey")

    @staticmethod
    def _validate_test(test):
        if not test:
            raise ValueError("Investigation test is required")
        if not isinstance(test, InvestigationTest):
            raise ValueError("Invalid investigation test")
        if not test.is_active:
            raise ValueError("Inactive investigation test cannot be used")

    @classmethod
    def create_order(
        cls,
        *,
        patient,
        ordered_visit=None,
        journey=None,
        priority=InvestigationOrder.PRIORITY_ROUTINE,
        order_notes=None,
        actor_user=None,
    ):
        cls._validate_patient(patient)
        cls._validate_visit(ordered_visit)
        cls._validate_journey(journey)

        if ordered_visit is not None and ordered_visit.patient_id != patient.id:
            raise ValueError("Ordered visit does not belong to patient")

        if journey is not None and journey.patient_id != patient.id:
            raise ValueError("Journey does not belong to patient")

        if priority not in InvestigationOrder.PRIORITIES:
            raise ValueError("Invalid investigation priority")

        order = InvestigationOrder(
            patient=patient,
            ordered_visit=ordered_visit,
            journey=journey,
            ordered_by_user=actor_user,
            priority=priority,
            order_notes=cls._clean(order_notes) or None,
            status=InvestigationOrder.STATUS_ORDERED,
        )

        db.session.add(order)
        db.session.commit()
        return order

    @staticmethod
    def next_sort_order(order):
        last_item = (
            InvestigationOrderItem.query.filter_by(order_id=order.id)
            .order_by(InvestigationOrderItem.sort_order.desc(), InvestigationOrderItem.id.desc())
            .first()
        )

        if not last_item:
            return 1

        return last_item.sort_order + 1

    @classmethod
    def add_order_item(
        cls,
        *,
        order,
        test,
        item_notes=None,
        sort_order=None,
    ):
        if not order:
            raise ValueError("Investigation order is required")

        if order.status == InvestigationOrder.STATUS_CANCELLED:
            raise ValueError("Cannot add item to cancelled investigation order")

        cls._validate_test(test)

        item = InvestigationOrderItem(
            order=order,
            test=test,
            status=InvestigationOrderItem.STATUS_PENDING_RESULT,
            item_notes=cls._clean(item_notes) or None,
            sort_order=sort_order if sort_order is not None else cls.next_sort_order(order),
        )

        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def cancel_order_item(item):
        if not item:
            raise ValueError("Investigation order item is required")

        item.status = InvestigationOrderItem.STATUS_CANCELLED
        db.session.commit()
        return item

    @classmethod
    def _update_order_status_from_items(cls, order):
        items = InvestigationOrderItem.query.filter_by(order_id=order.id).all()

        active_items = [
            item for item in items
            if item.status != InvestigationOrderItem.STATUS_CANCELLED
        ]

        if not active_items:
            order.status = InvestigationOrder.STATUS_CANCELLED
        elif all(item.status == InvestigationOrderItem.STATUS_REVIEWED for item in active_items):
            order.status = InvestigationOrder.STATUS_REVIEWED
        elif all(
            item.status in {
                InvestigationOrderItem.STATUS_RESULT_ENTERED,
                InvestigationOrderItem.STATUS_REVIEWED,
            }
            for item in active_items
        ):
            order.status = InvestigationOrder.STATUS_RESULTED
        elif any(
            item.status in {
                InvestigationOrderItem.STATUS_RESULT_ENTERED,
                InvestigationOrderItem.STATUS_REVIEWED,
            }
            for item in active_items
        ):
            order.status = InvestigationOrder.STATUS_PARTIALLY_RESULTED
        else:
            order.status = InvestigationOrder.STATUS_ORDERED

        db.session.commit()
        return order

    @classmethod
    def enter_result_for_order_item(
        cls,
        *,
        order_item,
        result_date,
        lab_name=None,
        result_value=None,
        unit=None,
        reference_range=None,
        result_text=None,
        doctor_comment=None,
        abnormal_flag=InvestigationResult.FLAG_UNKNOWN,
        has_attachment=False,
        attachment_label=None,
        external_report_reference=None,
        result_visit=None,
        actor_user=None,
    ):
        if not order_item:
            raise ValueError("Investigation order item is required")

        if order_item.status == InvestigationOrderItem.STATUS_CANCELLED:
            raise ValueError("Cannot enter result for cancelled investigation item")

        if not result_date:
            raise ValueError("Result date is required")

        cls._validate_visit(result_visit)

        order = order_item.order

        if result_visit is not None and result_visit.patient_id != order.patient_id:
            raise ValueError("Result visit does not belong to patient")

        if abnormal_flag not in InvestigationResult.ABNORMAL_FLAGS:
            raise ValueError("Invalid abnormal flag")

        result = InvestigationResult(
            patient_id=order.patient_id,
            test=order_item.test,
            order_item=order_item,
            ordered_visit=order.ordered_visit,
            result_visit=result_visit,
            result_date=result_date,
            lab_name=cls._clean(lab_name) or None,
            result_value=cls._clean(result_value) or None,
            unit=cls._clean(unit) or order_item.test.default_unit,
            reference_range=cls._clean(reference_range) or order_item.test.default_reference_range,
            result_text=cls._clean(result_text) or None,
            doctor_comment=cls._clean(doctor_comment) or None,
            abnormal_flag=abnormal_flag,
            status=InvestigationResult.STATUS_ENTERED,
            has_attachment=bool(has_attachment),
            attachment_label=cls._clean(attachment_label) or None,
            external_report_reference=cls._clean(external_report_reference) or None,
            entered_by_user=actor_user,
        )

        order_item.status = InvestigationOrderItem.STATUS_RESULT_ENTERED

        db.session.add(result)
        db.session.commit()

        cls._update_order_status_from_items(order)
        return result

    @classmethod
    def enter_historical_result(
        cls,
        *,
        patient,
        test,
        result_date,
        result_visit=None,
        lab_name=None,
        result_value=None,
        unit=None,
        reference_range=None,
        result_text=None,
        doctor_comment=None,
        abnormal_flag=InvestigationResult.FLAG_UNKNOWN,
        has_attachment=False,
        attachment_label=None,
        external_report_reference=None,
        actor_user=None,
    ):
        cls._validate_patient(patient)
        cls._validate_test(test)
        cls._validate_visit(result_visit)

        if result_visit is not None and result_visit.patient_id != patient.id:
            raise ValueError("Result visit does not belong to patient")

        if not result_date:
            raise ValueError("Result date is required")

        if abnormal_flag not in InvestigationResult.ABNORMAL_FLAGS:
            raise ValueError("Invalid abnormal flag")

        result = InvestigationResult(
            patient=patient,
            test=test,
            order_item=None,
            ordered_visit=None,
            result_visit=result_visit,
            result_date=result_date,
            lab_name=cls._clean(lab_name) or None,
            result_value=cls._clean(result_value) or None,
            unit=cls._clean(unit) or test.default_unit,
            reference_range=cls._clean(reference_range) or test.default_reference_range,
            result_text=cls._clean(result_text) or None,
            doctor_comment=cls._clean(doctor_comment) or None,
            abnormal_flag=abnormal_flag,
            status=InvestigationResult.STATUS_ENTERED,
            has_attachment=bool(has_attachment),
            attachment_label=cls._clean(attachment_label) or None,
            external_report_reference=cls._clean(external_report_reference) or None,
            entered_by_user=actor_user,
        )

        db.session.add(result)
        db.session.commit()
        return result

    @staticmethod
    def get_latest_result(patient, test):
        if not patient or not test:
            return None

        return (
            InvestigationResult.query.filter_by(
                patient_id=patient.id,
                test_id=test.id,
            )
            .filter(InvestigationResult.status != InvestigationResult.STATUS_CANCELLED)
            .order_by(InvestigationResult.result_date.desc(), InvestigationResult.id.desc())
            .first()
        )

    @staticmethod
    def list_latest_results(patient):
        if not patient:
            return []

        results = (
            InvestigationResult.query.filter_by(patient_id=patient.id)
            .filter(InvestigationResult.status != InvestigationResult.STATUS_CANCELLED)
            .order_by(InvestigationResult.result_date.desc(), InvestigationResult.id.desc())
            .all()
        )

        latest_by_test = {}
        for result in results:
            if result.test_id not in latest_by_test:
                latest_by_test[result.test_id] = result

        return list(latest_by_test.values())

    @staticmethod
    def list_pending_order_items(patient=None):
        query = InvestigationOrderItem.query.join(InvestigationOrder)

        if patient is not None:
            query = query.filter(InvestigationOrder.patient_id == patient.id)

        return (
            query.filter(
                InvestigationOrderItem.status.in_(
                    [
                        InvestigationOrderItem.STATUS_ORDERED,
                        InvestigationOrderItem.STATUS_PENDING_RESULT,
                    ]
                )
            )
            .order_by(InvestigationOrder.created_at.asc(), InvestigationOrderItem.sort_order.asc())
            .all()
        )

    @classmethod
    def find_missing_tests(cls, patient, required_tests):
        cls._validate_patient(patient)

        missing = []
        for test in required_tests:
            cls._validate_test(test)
            if cls.get_latest_result(patient, test) is None:
                missing.append(test)

        return missing

    @staticmethod
    def review_result(result, *, review_note=None, abnormal_flag=None, actor_user=None):
        if not result:
            raise ValueError("Investigation result is required")

        if abnormal_flag is not None:
            if abnormal_flag not in InvestigationResult.ABNORMAL_FLAGS:
                raise ValueError("Invalid abnormal flag")
            result.abnormal_flag = abnormal_flag

        result.status = InvestigationResult.STATUS_REVIEWED
        result.review_note = (review_note or "").strip() or None
        result.reviewed_by_user = actor_user
        result.reviewed_at = datetime.now(timezone.utc)

        if result.order_item:
            result.order_item.status = InvestigationOrderItem.STATUS_REVIEWED

        db.session.commit()

        if result.order_item:
            InvestigationService._update_order_status_from_items(result.order_item.order)

        return result
