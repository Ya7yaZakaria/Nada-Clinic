from datetime import date

from app.extensions import db
from app.models import Patient
from app.services.settings_service import SettingsService


class PatientService:
    """Patient domain service."""

    VALID_MARITAL_STATUSES = {
        "unknown",
        "single",
        "married",
        "divorced",
        "widowed",
    }

    @staticmethod
    def normalize_phone(phone):
        if phone is None:
            return ""

        return (
            str(phone)
            .strip()
            .replace(" ", "")
            .replace("-", "")
        )

    @staticmethod
    def generate_next_mrn():
        current_max = db.session.query(
            db.func.max(Patient.medical_file_number)
        ).scalar()

        if current_max is None:
            return 1

        return int(current_max) + 1

    @staticmethod
    def format_mrn(mrn):
        return f"{int(mrn):06d}"

    @staticmethod
    def parse_mrn_search(query):
        if query is None:
            return None

        cleaned = str(query).strip()

        if not cleaned:
            return None

        if cleaned.isdigit():
            return int(cleaned)

        return None

    @staticmethod
    def build_search_name(name_ar, name_en):
        return " ".join(
            part.strip().lower()
            for part in [name_ar or "", name_en or ""]
            if part and part.strip()
        )

    @staticmethod
    def validate_patient_data(data):
        name_ar = (data.get("name_ar") or "").strip()
        name_en = (data.get("name_en") or "").strip()
        phone_primary = PatientService.normalize_phone(data.get("phone_primary"))

        if not name_ar:
            raise ValueError("Arabic name is required.")

        if not name_en:
            raise ValueError("English name is required.")

        if not phone_primary:
            raise ValueError("Primary phone is required.")

        date_of_birth = data.get("date_of_birth")
        age_years_at_registration = data.get("age_years_at_registration")

        if not date_of_birth and age_years_at_registration in (None, ""):
            raise ValueError("Date of birth or manual age is required.")

        marital_status = data.get("marital_status") or "unknown"
        if marital_status not in PatientService.VALID_MARITAL_STATUSES:
            raise ValueError(f"Invalid marital status: {marital_status}")

    @staticmethod
    def create_patient(**data):
        PatientService.validate_patient_data(data)

        medical_file_number = data.get("medical_file_number")
        if medical_file_number is None:
            medical_file_number = PatientService.generate_next_mrn()

        phone_primary = PatientService.normalize_phone(data.get("phone_primary"))
        phone_secondary = PatientService.normalize_phone(data.get("phone_secondary"))

        age_years_at_registration = data.get("age_years_at_registration")
        age_recorded_at = data.get("age_recorded_at")

        if age_years_at_registration not in (None, ""):
            age_years_at_registration = int(age_years_at_registration)
            if age_recorded_at is None:
                age_recorded_at = date.today()
        else:
            age_years_at_registration = None
            age_recorded_at = None

        patient = Patient(
            medical_file_number=int(medical_file_number),
            name_ar=data["name_ar"].strip(),
            name_en=data["name_en"].strip(),
            search_name=PatientService.build_search_name(
                data["name_ar"],
                data["name_en"],
            ),
            gender=data.get("gender") or "female",
            date_of_birth=data.get("date_of_birth"),
            age_years_at_registration=age_years_at_registration,
            age_recorded_at=age_recorded_at,
            marital_status=data.get("marital_status") or "unknown",
            is_virgin=bool(data.get("is_virgin", False)),
            occupation=data.get("occupation"),
            phone_primary=phone_primary,
            phone_secondary=phone_secondary or None,
            email=data.get("email"),
            governorate=data.get("governorate"),
            city=data.get("city"),
            street=data.get("street"),
            is_active=bool(data.get("is_active", True)),
        )

        db.session.add(patient)
        db.session.commit()

        return patient

    @staticmethod
    def update_patient(patient, **data):
        PatientService.validate_patient_data(
            {
                "name_ar": data.get("name_ar", patient.name_ar),
                "name_en": data.get("name_en", patient.name_en),
                "phone_primary": data.get("phone_primary", patient.phone_primary),
                "date_of_birth": data.get("date_of_birth", patient.date_of_birth),
                "age_years_at_registration": data.get(
                    "age_years_at_registration",
                    patient.age_years_at_registration,
                ),
                "marital_status": data.get("marital_status", patient.marital_status),
            }
        )

        editable_fields = [
            "name_ar",
            "name_en",
            "gender",
            "date_of_birth",
            "age_years_at_registration",
            "age_recorded_at",
            "marital_status",
            "is_virgin",
            "occupation",
            "phone_primary",
            "phone_secondary",
            "email",
            "governorate",
            "city",
            "street",
            "is_active",
        ]

        for field in editable_fields:
            if field not in data:
                continue

            value = data[field]

            if field in ("phone_primary", "phone_secondary"):
                value = PatientService.normalize_phone(value) or None

            setattr(patient, field, value)

        patient.search_name = PatientService.build_search_name(
            patient.name_ar,
            patient.name_en,
        )

        db.session.commit()

        return patient

    @staticmethod
    def change_medical_file_number(patient, new_mrn):
        new_mrn = int(new_mrn)

        existing_patient = Patient.query.filter_by(
            medical_file_number=new_mrn
        ).first()

        if existing_patient and existing_patient.id != patient.id:
            raise ValueError("Medical file number already exists.")

        patient.medical_file_number = new_mrn
        db.session.commit()

        return patient

    @staticmethod
    def calculate_display_age(patient, reference_date=None):
        reference_date = reference_date or date.today()

        if patient.date_of_birth:
            return PatientService._completed_years(
                patient.date_of_birth,
                reference_date,
            )

        if patient.age_years_at_registration is not None and patient.age_recorded_at:
            years_passed = PatientService._completed_years(
                patient.age_recorded_at,
                reference_date,
            )
            return patient.age_years_at_registration + years_passed

        return None

    @staticmethod
    def _completed_years(start_date, reference_date):
        years = reference_date.year - start_date.year

        if (reference_date.month, reference_date.day) < (
            start_date.month,
            start_date.day,
        ):
            years -= 1

        return years

    @staticmethod
    def get_display_name(patient, language=None):
        language = language or SettingsService.get(
            "localization.language",
            default="en",
            cast=True,
        )

        if str(language).lower().startswith("ar"):
            return patient.name_ar

        return patient.name_en

    @staticmethod
    def get_full_address(patient):
        return " / ".join(
            part.strip()
            for part in [
                patient.governorate or "",
                patient.city or "",
                patient.street or "",
            ]
            if part and part.strip()
        )

    @staticmethod
    def find_duplicate_phone_patients(phone, exclude_patient_id=None):
        normalized_phone = PatientService.normalize_phone(phone)

        query = Patient.query.filter(
            db.or_(
                Patient.phone_primary == normalized_phone,
                Patient.phone_secondary == normalized_phone,
            )
        )

        if exclude_patient_id is not None:
            query = query.filter(Patient.id != exclude_patient_id)

        return query.order_by(Patient.created_at.desc()).all()

    @staticmethod
    def get_recent_patients(limit=10):
        return (
            Patient.query.filter_by(is_active=True)
            .order_by(Patient.created_at.desc(), Patient.id.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def search_patients(query, limit=20):
        cleaned_query = (query or "").strip()

        if not cleaned_query:
            return PatientService.get_recent_patients(limit=limit)

        normalized_phone = PatientService.normalize_phone(cleaned_query)
        lowered_query = cleaned_query.lower()
        mrn_value = PatientService.parse_mrn_search(cleaned_query)

        filters = [
            Patient.name_ar.ilike(f"%{cleaned_query}%"),
            Patient.name_en.ilike(f"%{cleaned_query}%"),
            Patient.search_name.ilike(f"%{lowered_query}%"),
            Patient.phone_primary.ilike(f"%{normalized_phone}%"),
            Patient.phone_secondary.ilike(f"%{normalized_phone}%"),
        ]

        if mrn_value is not None:
            filters.append(Patient.medical_file_number == mrn_value)

        return (
            Patient.query.filter(
                Patient.is_active.is_(True),
                db.or_(*filters),
            )
            .order_by(Patient.created_at.desc(), Patient.id.desc())
            .limit(limit)
            .all()
        )
