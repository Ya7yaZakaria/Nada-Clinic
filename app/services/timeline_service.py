from datetime import date, datetime, time

from app.models.investigation import InvestigationOrder, InvestigationResult
from app.models.surgery import SurgeryCase


class TimelineService:
    """Generated patient timeline service.

    No timeline table is used. Timeline events are generated from existing
    clinical records such as Visits, Journeys, and Investigations.
    """

    @staticmethod
    def normalize_event_date(value):
        if isinstance(value, datetime):
            return value

        if isinstance(value, date):
            return datetime.combine(value, time.min)

        raise ValueError("Timeline event date must be date or datetime.")

    @staticmethod
    def get_patient_timeline(patient):
        events = []
        events.extend(TimelineService.build_journey_events(patient))
        events.extend(TimelineService.build_visit_events(patient))
        events.extend(TimelineService.build_investigation_events(patient))
        events.extend(TimelineService.build_surgery_events(patient))
        return TimelineService.sort_events(events)

    @staticmethod
    def build_journey_events(patient):
        events = []

        for journey in patient.journeys.all():
            events.append(
                {
                    "date": TimelineService.normalize_event_date(journey.start_date),
                    "type": "journey_started",
                    "label": "Journey started",
                    "title": journey.title,
                    "subtitle": journey.journey_type,
                    "source": "journey",
                    "source_uuid": journey.uuid,
                    "status": journey.status,
                }
            )

            if journey.status == "closed" and journey.end_date:
                events.append(
                    {
                        "date": TimelineService.normalize_event_date(journey.end_date),
                        "type": "journey_closed",
                        "label": "Journey closed",
                        "title": journey.title,
                        "subtitle": journey.outcome or "closed",
                        "source": "journey",
                        "source_uuid": journey.uuid,
                        "status": journey.status,
                    }
                )

        return events

    @staticmethod
    def build_visit_events(patient):
        events = []

        for visit in patient.visits.all():
            events.append(
                {
                    "date": TimelineService.normalize_event_date(visit.visit_date),
                    "type": "visit",
                    "label": "Visit",
                    "title": visit.visit_type,
                    "subtitle": visit.status,
                    "source": "visit",
                    "source_uuid": visit.uuid,
                    "status": visit.status,
                    "is_unassigned": visit.journey_id is None,
                }
            )

            if visit.completed_at:
                events.append(
                    {
                        "date": TimelineService.normalize_event_date(visit.completed_at),
                        "type": "visit_completed",
                        "label": "Visit completed",
                        "title": visit.visit_type,
                        "subtitle": "completed",
                        "source": "visit",
                        "source_uuid": visit.uuid,
                        "status": visit.status,
                        "is_unassigned": visit.journey_id is None,
                    }
                )

            if visit.reopened_at:
                events.append(
                    {
                        "date": TimelineService.normalize_event_date(visit.reopened_at),
                        "type": "visit_reopened",
                        "label": "Visit reopened",
                        "title": visit.visit_type,
                        "subtitle": "reopened",
                        "source": "visit",
                        "source_uuid": visit.uuid,
                        "status": visit.status,
                        "is_unassigned": visit.journey_id is None,
                    }
                )

        return events

    @staticmethod
    def build_surgery_events(patient):
        events = []

        surgeries = (
            SurgeryCase.query.filter_by(patient_id=patient.id, is_active=True)
            .order_by(SurgeryCase.scheduled_at.desc(), SurgeryCase.id.desc())
            .all()
        )

        for surgery in surgeries:
            events.append(
                {
                    "date": TimelineService.normalize_event_date(surgery.scheduled_at),
                    "type": "surgery",
                    "label": "Surgery",
                    "title": surgery.procedure_name,
                    "subtitle": surgery.status,
                    "source": "surgery",
                    "source_uuid": surgery.uuid,
                    "status": surgery.status,
                    "badge_class": "surgery",
                }
            )

            if surgery.completed_at:
                events.append(
                    {
                        "date": TimelineService.normalize_event_date(surgery.completed_at),
                        "type": "surgery_completed",
                        "label": "Surgery completed",
                        "title": surgery.procedure_name,
                        "subtitle": surgery.status,
                        "source": "surgery",
                        "source_uuid": surgery.uuid,
                        "status": surgery.status,
                        "badge_class": "surgery",
                    }
                )

        return events

    @staticmethod
    def build_investigation_events(patient):
        events = []

        orders = (
            InvestigationOrder.query.filter_by(patient_id=patient.id)
            .order_by(InvestigationOrder.created_at.desc(), InvestigationOrder.id.desc())
            .all()
        )

        for order in orders:
            events.append(
                {
                    "date": TimelineService.normalize_event_date(order.created_at),
                    "type": "investigation_ordered",
                    "label": "Investigation ordered",
                    "title": f"Investigation order ({order.status})",
                    "subtitle": order.priority,
                    "source": "investigation_order",
                    "source_uuid": order.uuid,
                    "status": order.status,
                }
            )

        results = (
            InvestigationResult.query.filter_by(patient_id=patient.id)
            .filter(InvestigationResult.status != InvestigationResult.STATUS_CANCELLED)
            .order_by(InvestigationResult.result_date.desc(), InvestigationResult.id.desc())
            .all()
        )

        for result in results:
            events.append(
                {
                    "date": TimelineService.normalize_event_date(result.result_date),
                    "type": "investigation_result_entered",
                    "label": "Investigation result",
                    "title": result.test.name_en,
                    "subtitle": result.abnormal_flag,
                    "source": "investigation_result",
                    "source_uuid": result.uuid,
                    "status": result.status,
                }
            )

            if result.status == InvestigationResult.STATUS_REVIEWED and result.reviewed_at:
                events.append(
                    {
                        "date": TimelineService.normalize_event_date(result.reviewed_at),
                        "type": "investigation_result_reviewed",
                        "label": "Investigation result reviewed",
                        "title": result.test.name_en,
                        "subtitle": result.review_note or result.abnormal_flag,
                        "source": "investigation_result",
                        "source_uuid": result.uuid,
                        "status": result.status,
                    }
                )

        return events

    @staticmethod
    def sort_events(events):
        return sorted(
            events,
            key=lambda event: event["date"],
            reverse=True,
        )
