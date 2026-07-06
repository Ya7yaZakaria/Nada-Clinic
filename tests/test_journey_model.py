from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Journey, Patient, User
from app.services.journey_service import JourneyService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_patient(**overrides):
    data = {
        "name_ar": "سارة أحمد",
        "name_en": "Sara Ahmed",
        "phone_primary": "01000000000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def test_journey_can_be_created_for_patient():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy 2026",
            start_date="2026",
        )

        assert journey.id is not None
        assert journey.uuid is not None
        assert journey.patient_id == patient.id
        assert journey.status == "active"
        assert journey.start_date == date(2026, 1, 1)

        db.drop_all()


def test_flexible_date_accepts_year_month_and_day():
    assert JourneyService.parse_flexible_date("2026") == (date(2026, 1, 1), "year")
    assert JourneyService.parse_flexible_date("2026-07") == (date(2026, 7, 1), "month")
    assert JourneyService.parse_flexible_date("2026-07-07") == (date(2026, 7, 7), "day")


def test_journey_rejects_invalid_type():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        with pytest.raises(ValueError, match="Invalid journey type"):
            JourneyService.create_journey(
                patient=patient,
                journey_type="wrong",
                title="Wrong",
                start_date="2026",
            )

        db.drop_all()


def test_only_one_active_journey_per_type():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy 1",
            start_date="2026",
        )

        with pytest.raises(ValueError, match="already has an active pregnancy journey"):
            JourneyService.create_journey(
                patient=patient,
                journey_type="pregnancy",
                title="Pregnancy 2",
                start_date="2027",
            )

        db.drop_all()


def test_patient_can_have_multiple_active_different_journey_types():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        pregnancy = JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy",
            start_date="2026",
        )
        gyn = JourneyService.create_journey(
            patient=patient,
            journey_type="gynecology",
            title="Gyn problem",
            start_date="2026-03",
        )

        assert pregnancy.status == "active"
        assert gyn.status == "active"
        assert Journey.query.count() == 2

        db.drop_all()


def test_close_journey_requires_valid_outcome_for_type():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy",
            start_date="2026",
        )

        with pytest.raises(ValueError, match="Invalid outcome"):
            JourneyService.close_journey(
                journey,
                outcome="surgery_done",
                end_date="2026",
            )

        db.drop_all()


def test_lost_to_follow_up_valid_for_all_journey_types():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        for journey_type in ["pregnancy", "gynecology", "infertility"]:
            journey = JourneyService.create_journey(
                patient=patient,
                journey_type=journey_type,
                title=f"{journey_type} journey",
                start_date="2026",
            )
            JourneyService.close_journey(
                journey,
                outcome="lost_to_follow_up",
                end_date="2026",
                outcome_note="Patient stopped attending.",
            )

            assert journey.status == "closed"
            assert journey.outcome == "lost_to_follow_up"

        db.drop_all()


def test_close_journey_stores_outcome_note_and_year_precision():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="infertility",
            title="Infertility treatment",
            start_date="2025",
        )

        JourneyService.close_journey(
            journey,
            outcome="pregnancy_after_treatment",
            end_date="2026",
            outcome_note="Positive pregnancy test.",
        )

        assert journey.status == "closed"
        assert journey.end_date == date(2026, 1, 1)
        assert journey.end_date_precision == "year"
        assert journey.outcome == "pregnancy_after_treatment"
        assert journey.outcome_note == "Positive pregnancy test."

        db.drop_all()


def test_reopen_journey_clears_end_and_outcome_fields():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="gynecology",
            title="Bleeding",
            start_date="2026",
        )

        JourneyService.close_journey(
            journey,
            outcome="resolved",
            end_date="2026-07",
            outcome_note="Improved.",
        )
        JourneyService.reopen_journey(journey)

        assert journey.status == "active"
        assert journey.end_date is None
        assert journey.end_date_precision is None
        assert journey.outcome is None
        assert journey.outcome_note is None

        db.drop_all()


def test_multiple_closed_journeys_same_type_allowed():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        first = JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy 1",
            start_date="2024",
        )
        JourneyService.close_journey(
            first,
            outcome="delivered",
            end_date="2025",
        )

        second = JourneyService.create_journey(
            patient=patient,
            journey_type="pregnancy",
            title="Pregnancy 2",
            start_date="2026",
        )

        assert first.status == "closed"
        assert second.status == "active"

        db.drop_all()


def test_journey_can_exist_without_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        journey = JourneyService.create_journey(
            patient=patient,
            journey_type="gynecology",
            title="Pain follow-up",
            start_date="2026",
        )

        assert journey.id is not None
        assert journey.visits.count() == 0

        db.drop_all()


def test_get_active_and_latest_journeys():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        first = JourneyService.create_journey(
            patient=patient,
            journey_type="gynecology",
            title="Old",
            start_date="2025",
        )
        JourneyService.close_journey(first, outcome="resolved", end_date="2025")

        second = JourneyService.create_journey(
            patient=patient,
            journey_type="gynecology",
            title="Current",
            start_date="2026",
        )

        active = JourneyService.get_active_journeys(patient)
        latest = JourneyService.get_latest_journey(patient, "gynecology")

        assert active == [second]
        assert latest == second

        db.drop_all()

