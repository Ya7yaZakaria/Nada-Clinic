"""Shared test helpers extracted from exact duplicate setup code."""

from datetime import date
from io import BytesIO
from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User
from app.models.drug import Drug
from app.models.drug_dictionary import (
    DrugCategory,
    DrugForm,
    DrugRoute,
    DrugSafetyStatus,
)
from app.models.investigation import InvestigationTest
from app.models.visit import Visit
from app.services.drug_service import DrugService
from app.services.investigation_dictionary_service import (
    InvestigationDictionaryService,
)
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.visit_service import VisitService


def set_test_password(user, password="12345678"):
    """Assign a valid low-cost hash for test credentials."""
    user.password_hash = generate_password_hash(
        password,
        method="pbkdf2:sha256:1000",
        salt_length=8,
    )
    return user


def create_basic_drug():
    form = DrugForm(code="tablet", name_en="Tablet")
    route = DrugRoute(code="oral", name_en="Oral")
    db.session.add_all([form, route])
    db.session.commit()

    drug = Drug(
        generic_name="Levofloxacin",
        trade_name="Tavanic",
        strength="500 mg",
        form=form,
        route=route,
    )
    db.session.add(drug)
    db.session.commit()
    return drug, route


def create_basic_patient(**overrides):
    data = {
        "name_ar": "سارة أحمد",
        "name_en": "Sara Ahmed",
        "phone_primary": "01000000000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_configurable_drug(active=True, trade_name="Tavanic", code_suffix=""):
    form = DrugForm(code=f"tablet{code_suffix}", name_en=f"Tablet{code_suffix}")
    route = DrugRoute(code=f"oral{code_suffix}", name_en=f"Oral{code_suffix}")
    db.session.add_all([form, route])
    db.session.commit()

    drug = Drug(
        generic_name="Levofloxacin",
        trade_name=trade_name,
        strength="500 mg",
        form=form,
        route=route,
        is_active=active,
    )
    db.session.add(drug)
    db.session.commit()

    return drug, route


def create_drug_dictionary_items():
    category = DrugCategory(code="antibiotic", name_en="Antibiotic")
    form = DrugForm(code="tablet", name_en="Tablet")
    injection_form = DrugForm(code="injection", name_en="Injection")
    route = DrugRoute(code="oral", name_en="Oral")
    pregnancy_status = DrugSafetyStatus(code="caution", name_en="Caution", severity_order=2)
    lactation_status = DrugSafetyStatus(code="safe", name_en="Safe", severity_order=1)

    db.session.add_all([category, form, injection_form, route, pregnancy_status, lactation_status])
    db.session.commit()

    return {
        "category": category,
        "form": form,
        "injection_form": injection_form,
        "route": route,
        "pregnancy_status": pregnancy_status,
        "lactation_status": lactation_status,
    }


def create_drug_via_service():
    form = DrugForm(code="tablet", name_en="Tablet")
    route = DrugRoute(code="oral", name_en="Oral")
    db.session.add_all([form, route])
    db.session.commit()

    drug = DrugService.create_drug(
        generic_name="Levofloxacin",
        trade_name="Tavanic",
        strength="500 mg",
        form=form,
        route=route,
    )
    return drug, route


def create_full_patient(**overrides):
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


def create_investigation_patient(**overrides):
    data = {
        "name_ar": "منى علي",
        "name_en": "Mona Ali",
        "phone_primary": "01066440000",
        "date_of_birth": date(1996, 7, 1),
    }
    data.update(overrides)
    return PatientService.create_patient(**data)


def create_investigation_test_amh(code="amh", name="AMH"):
    category = InvestigationDictionaryService.create_category(
        code=f"{code}_category",
        name_en=f"{name} Category",
    )
    return InvestigationDictionaryService.create_test(
        code=code,
        name_en=name,
        category=category,
        default_unit="mIU/L",
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def create_investigation_test_tsh(code="tsh", name="TSH"):
    category = InvestigationDictionaryService.create_category(code=f"{code}_category", name_en=f"{name} Category")
    return InvestigationDictionaryService.create_test(
        code=code,
        name_en=name,
        category=category,
        default_unit="mIU/L",
        default_reference_range="0.4-4.0",
        result_kind=InvestigationTest.RESULT_KIND_NUMERIC,
    )


def create_investigation_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Investigation visit",
    )


def create_prescription_patient(**overrides):
    data = {
        "name_ar": "??? ???",
        "name_en": "Mona Ali",
        "phone_primary": "01011112222",
        "date_of_birth": date(1996, 7, 1),
        "governorate": "Qalyubia",
        "city": "Benha",
        "street": "Main Street",
    }
    data.update(overrides)

    return PatientService.create_patient(**data)


def create_prescription_visit(patient):
    visit = Visit(
        patient=patient,
        visit_type="gyn",
        visit_date=date(2026, 7, 13),
    )
    db.session.add(visit)
    db.session.commit()
    return visit


def create_role_user(role, email, phone):
    user = User(
        email=email,
        phone=phone,
        name=f"{role} User",
    )
    set_test_password(user, "12345678")

    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role)

    return user


def create_user(email, phone, role_name, name="Test User"):
    user = User(email=email, phone=phone, name=name)
    set_test_password(user, "12345678")
    db.session.add(user)
    db.session.commit()
    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)
    return user


def create_user_email_role_phone(email, role_name, phone):
    user = User(email=email, phone=phone, name=role_name)
    set_test_password(user, "12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)
    return user


def create_user_named_for_role(email, phone, role_name):
    user = User(email=email, phone=phone, name=role_name)
    set_test_password(user, "12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)

    return user


def create_visit_with_pelvic_pain(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="Pelvic pain",
    )


def login(client, email):
    return client.post("/auth/login", data={"login_identifier": email, "password": "12345678"})


def login_follow_redirects(client, email):
    return client.post(
        "/auth/login",
        data={"login_identifier": email, "password": "12345678"},
        follow_redirects=True,
    )


def make_app():
    return create_app("testing")


def make_app_csrf_disabled():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost", WTF_CSRF_ENABLED=False)
    return app


def make_app_server():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def make_app_with_upload_tmp_path(tmp_path):
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
        PATIENT_DOCUMENT_UPLOAD_FOLDER=str(tmp_path / "uploads" / "patient_documents"),
        PATIENT_DOCUMENT_MAX_FILE_SIZE_BYTES=1024 * 1024,
    )
    return app


def make_file(filename="report.pdf", content=b"fake pdf content", content_type="application/pdf"):
    return FileStorage(
        stream=BytesIO(content),
        filename=filename,
        content_type=content_type,
    )


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (_PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
