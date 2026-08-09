from tests.factories import create_investigation_visit as create_visit
from tests.factories import make_app_csrf_disabled as make_app

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


def create_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01066110000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


