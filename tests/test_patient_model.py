import uuid
from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Patient
from app.services.patient_service import PatientService
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
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return PatientService.create_patient(**data)


def test_patient_can_be_created():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        assert patient.id is not None
        assert patient.name_ar == "سارة أحمد"
        assert patient.name_en == "Sara Ahmed"
        assert patient.phone_primary == "01000000000"
        assert patient.is_active is True

        db.drop_all()


def test_patient_uuid_is_generated():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        parsed_uuid = uuid.UUID(patient.uuid)

        assert str(parsed_uuid) == patient.uuid

        db.drop_all()


def test_mrn_generated_as_integer_and_formatted():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        assert patient.medical_file_number == 1
        assert patient.formatted_mrn == "000001"
        assert PatientService.format_mrn(patient.medical_file_number) == "000001"

        db.drop_all()


def test_mrn_is_unique_and_increments():
    app = make_app()

    with app.app_context():
        db.create_all()

        first = create_patient(phone_primary="01000000001")
        second = create_patient(phone_primary="01000000002")

        assert first.medical_file_number == 1
        assert second.medical_file_number == 2
        assert first.medical_file_number != second.medical_file_number

        db.drop_all()


def test_arabic_and_english_names_are_required():
    app = make_app()

    with app.app_context():
        db.create_all()

        with pytest.raises(ValueError):
            create_patient(name_ar="")

        with pytest.raises(ValueError):
            create_patient(name_en="")

        db.drop_all()


def test_primary_phone_is_required():
    app = make_app()

    with app.app_context():
        db.create_all()

        with pytest.raises(ValueError):
            create_patient(phone_primary="")

        db.drop_all()


def test_dob_or_manual_age_is_required():
    app = make_app()

    with app.app_context():
        db.create_all()

        with pytest.raises(ValueError):
            create_patient(date_of_birth=None, age_years_at_registration=None)

        patient = create_patient(
            date_of_birth=None,
            age_years_at_registration=30,
            age_recorded_at=date(2026, 7, 1),
        )

        assert patient.age_years_at_registration == 30

        db.drop_all()


def test_phone_duplicate_is_allowed_and_detectable():
    app = make_app()

    with app.app_context():
        db.create_all()

        first = create_patient(phone_primary="01000000001")
        second = create_patient(
            name_ar="منى أحمد",
            name_en="Mona Ahmed",
            phone_primary="01000000001",
        )

        duplicates = PatientService.find_duplicate_phone_patients("01000000001")

        assert first.id != second.id
        assert len(duplicates) == 2

        db.drop_all()


def test_age_calculation_from_dob():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(date_of_birth=date(1996, 7, 1))

        assert PatientService.calculate_display_age(
            patient,
            reference_date=date(2026, 7, 7),
        ) == 30

        db.drop_all()


def test_manual_age_fallback_updates_with_years_passed():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(
            date_of_birth=None,
            age_years_at_registration=30,
            age_recorded_at=date(2026, 7, 1),
        )

        assert PatientService.calculate_display_age(
            patient,
            reference_date=date(2028, 7, 2),
        ) == 32

        db.drop_all()


def test_defaults_are_applied():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient()

        assert patient.gender == "female"
        assert patient.marital_status == "unknown"
        assert patient.is_virgin is False
        assert patient.is_active is True

        db.drop_all()


def test_virgin_check_can_be_true():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(is_virgin=True)

        assert patient.is_virgin is True

        db.drop_all()


def test_address_display_uses_governorate_city_street_only():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(
            governorate="Cairo",
            city="Nasr City",
            street="Abbas El Akkad",
        )

        assert PatientService.get_full_address(patient) == "Cairo / Nasr City / Abbas El Akkad"

        db.drop_all()


def test_search_name_contains_arabic_and_english_names():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(name_ar="سارة أحمد", name_en="Sara Ahmed")

        assert "سارة أحمد" in patient.search_name
        assert "sara ahmed" in patient.search_name

        db.drop_all()


def test_display_name_follows_language_setting():
    app = make_app()

    with app.app_context():
        db.create_all()

        SettingsService.seed_defaults()
        patient = create_patient(name_ar="سارة أحمد", name_en="Sara Ahmed")

        assert PatientService.get_display_name(patient, language="en") == "Sara Ahmed"
        assert PatientService.get_display_name(patient, language="ar") == "سارة أحمد"

        SettingsService.set("localization.language", "ar")

        assert PatientService.get_display_name(patient) == "سارة أحمد"

        db.drop_all()


def test_change_medical_file_number_without_audit_table():
    app = make_app()

    with app.app_context():
        db.create_all()

        first = create_patient(phone_primary="01000000001")
        second = create_patient(phone_primary="01000000002")

        PatientService.change_medical_file_number(first, 10)

        assert first.medical_file_number == 10
        assert first.formatted_mrn == "000010"

        with pytest.raises(ValueError):
            PatientService.change_medical_file_number(second, 10)

        assert Patient.query.count() == 2

        db.drop_all()
