from datetime import date, datetime, time


class TimelineService:
    """Generated patient timeline service.

    No timeline table is used. Timeline events are generated from existing
    clinical records such as Visits and Journeys.
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
    def sort_events(events):
        return sorted(
            events,
            key=lambda event: event["date"],
            reverse=True,
        )
