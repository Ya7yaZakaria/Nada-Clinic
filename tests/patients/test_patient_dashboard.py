from tests.factories import login_follow_redirects as login, set_test_password
from tests.factories import make_app_server as make_app

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from flask import g

from app import create_app
from app.extensions import db
from app.models import Appointment, FinanceCharge, InvestigationResult, InvestigationTest, Journey, User, Visit
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


def create_user(email, phone, role_name):
    user = User(email=email, phone=phone, name=f"{role_name} User")
    set_test_password(user, "12345678")
    db.session.add(user)
    db.session.commit()
    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)
    return user


def create_patient(index, *, active=True):
    return PatientService.create_patient(
        name_ar=f"مريضة {index}",
        name_en=f"Patient {index}",
        phone_primary=f"01090{index:06d}",
        date_of_birth=date(1990, 1, 1),
        is_active=active,
    )


def test_patient_hub_renders_real_kpis_and_operational_sections():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-hub@example.com", "01030100001", "Doctor")
        patient = create_patient(1)
        db.session.add(
            Visit(
                patient_id=patient.id,
                visit_type="general",
                status="completed",
                visit_date=datetime.now(timezone.utc) - timedelta(days=4),
            )
        )
        db.session.commit()

        with app.test_client() as client:
            login(client, "doctor-hub@example.com")
            response = client.get("/patients/")

        assert response.status_code == 200
        assert b"Patient command center" in response.data
        assert b"Active patients" in response.data
        assert b"Seen in 30 days" in response.data
        assert b"New registrations" in response.data
        assert b"Active care journeys" in response.data
        assert b"Patient 1" in response.data
        assert b"Open workspace" in response.data
        assert b"patient-hub.css" in response.data
        db.drop_all()


def test_directory_filters_by_active_journey_and_upcoming_appointment():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-filter@example.com", "01030100002", "Doctor")
        pregnancy_patient = create_patient(2)
        gyne_patient = create_patient(3)
        db.session.add_all(
            [
                Journey(
                    patient_id=pregnancy_patient.id,
                    journey_type="pregnancy",
                    status="active",
                    title="Current pregnancy",
                    start_date=date.today(),
                ),
                Journey(
                    patient_id=gyne_patient.id,
                    journey_type="gynecology",
                    status="active",
                    title="Gyne follow-up",
                    start_date=date.today(),
                ),
                Appointment(
                    patient_id=pregnancy_patient.id,
                    appointment_date=date.today() + timedelta(days=2),
                    appointment_type="follow_up",
                    status="booked",
                    source="clinic",
                ),
            ]
        )
        db.session.commit()

        with app.test_client() as client:
            login(client, "doctor-filter@example.com")
            response = client.get(
                "/patients/search?journey=pregnancy&upcoming=1&status=active"
            )

        assert response.status_code == 200
        assert b"Patient 2" in response.data
        assert b"Patient 3" not in response.data
        assert b"Pregnancy" in response.data
        assert b"No upcoming booking" not in response.data
        db.drop_all()


def test_attention_filters_and_badges_use_real_clinical_and_finance_data():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        doctor = create_user("doctor-attention@example.com", "01030100003", "Doctor")
        patient = create_patient(4)
        other_patient = create_patient(5)
        test = InvestigationTest(code="CBC-HUB", name_en="CBC", result_kind="text")
        db.session.add(test)
        db.session.flush()
        db.session.add_all(
            [
                InvestigationResult(
                    patient_id=patient.id,
                    test_id=test.id,
                    result_date=date.today(),
                    result_text="Available",
                    status="entered",
                    abnormal_flag="unknown",
                    entered_by_user_id=doctor.id,
                ),
                FinanceCharge(
                    patient_id=patient.id,
                    source_type="manual",
                    service_type="consultation",
                    title="Consultation",
                    gross_amount=Decimal("500"),
                    net_amount=Decimal("500"),
                    paid_amount=Decimal("200"),
                    remaining_amount=Decimal("300"),
                    status="partial",
                    service_date=date.today(),
                ),
            ]
        )
        db.session.commit()

        with app.test_client() as client:
            login(client, "doctor-attention@example.com")
            response = client.get(
                "/patients/search?pending_results=1&outstanding=1&status=active"
            )

        assert response.status_code == 200
        assert b"Patient 4" in response.data
        assert b"Patient 5" not in response.data
        assert b"1 review" in response.data
        assert b"300 EGP" in response.data
        db.drop_all()


def test_reception_directory_does_not_expose_clinical_journey_or_review_data():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-hub@example.com", "01030100004", "Reception")
        patient = create_patient(6)
        db.session.add(
            Journey(
                patient_id=patient.id,
                journey_type="infertility",
                status="active",
                title="Private clinical journey",
                start_date=date.today(),
            )
        )
        db.session.commit()

        with app.test_client() as client:
            login(client, "reception-hub@example.com")
            response = client.get("/patients/")

        assert response.status_code == 200
        assert b"Operational view" in response.data
        assert b"Private clinical journey" not in response.data
        assert b"Pending review" not in response.data
        assert b"Book appointment" in response.data
        assert b"Start new visit" not in response.data
        db.drop_all()


def test_directory_paginates_without_loading_the_whole_patient_table():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("admin-pages@example.com", "01030100005", "Admin")
        for index in range(30, 52):
            create_patient(index)

        with app.test_client() as client:
            login(client, "admin-pages@example.com")
            response = client.get("/patients/search?sort=mrn&page=2")

        assert response.status_code == 200
        assert b"Page 2 of 2" in response.data
        assert b"Patient 50" in response.data
        assert b"Patient 30" not in response.data
        db.drop_all()


def test_patient_search_is_in_topbar_and_kpis_open_quick_lists():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-topbar@example.com", "01030100006", "Doctor")
        create_patient(60)

        with app.test_client() as client:
            login(client, "doctor-topbar@example.com")
            response = client.get("/patients/")

        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'class="patient-topbar-search"' in html
        assert 'hx-get="/patients/global-search"' in html
        assert 'id="patient-directory-search"' in html
        assert html.index('class="patient-topbar-search"') < html.index('class="topbar-actions"')
        assert 'data-bs-target="#patientQuickList"' in html
        assert '/patients/quick-list?cohort=active' in html
        assert '/patients/quick-list?cohort=new_this_month' in html
        assert '/patients/quick-list?cohort=seen_30_days' in html
        assert '/patients/quick-list?cohort=attention' in html
        db.drop_all()


def test_quick_lists_return_real_cohorts_and_patient_actions():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-drawer@example.com", "01030100007", "Doctor")
        recent_patient = create_patient(61)
        older_patient = create_patient(62)
        older_patient.created_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        db.session.add(
            Visit(
                patient_id=recent_patient.id,
                visit_type="general",
                status="completed",
                visit_date=datetime.now(timezone.utc) - timedelta(days=3),
            )
        )
        db.session.commit()

        with app.test_client() as client:
            login(client, "doctor-drawer@example.com")
            new_response = client.get("/patients/quick-list?cohort=new_this_month")
            seen_response = client.get("/patients/quick-list?cohort=seen_30_days")

        assert new_response.status_code == 200
        assert b"New this month" in new_response.data
        assert b"Patient 61" in new_response.data
        assert b"Patient 62" not in new_response.data
        assert b"Open patient" in new_response.data
        assert seen_response.status_code == 200
        assert b"Seen in 30 days" in seen_response.data
        assert b"Patient 61" in seen_response.data
        assert b"Patient 62" not in seen_response.data
        db.drop_all()


def test_journey_quick_list_returns_only_matching_clinical_patients():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-journey-drawer@example.com", "01030100008", "Doctor")
        pregnancy_patient = create_patient(63)
        other_patient = create_patient(64)
        db.session.add(
            Journey(
                patient_id=pregnancy_patient.id,
                journey_type="pregnancy",
                status="active",
                title="Sensitive pregnancy care",
                start_date=date.today(),
            )
        )
        db.session.commit()

        with app.test_client() as client:
            login(client, "doctor-journey-drawer@example.com")
            doctor_response = client.get("/patients/quick-list?journey=pregnancy")

        assert doctor_response.status_code == 200
        assert b"Pregnancy journeys" in doctor_response.data
        assert b"Patient 63" in doctor_response.data
        assert b"Patient 64" not in doctor_response.data
        db.drop_all()


def test_reception_cannot_use_journey_quick_list_to_expose_clinical_data():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-drawer@example.com", "01030100009", "Reception")
        patient = create_patient(65)
        db.session.add(
            Journey(
                patient_id=patient.id,
                journey_type="pregnancy",
                status="active",
                title="Sensitive pregnancy care",
                start_date=date.today(),
            )
        )
        db.session.commit()

        with app.test_client() as client:
            login(client, "reception-drawer@example.com")
            response = client.get("/patients/quick-list?journey=pregnancy")

        assert response.status_code == 200
        assert b"Pregnancy journeys" not in response.data
        assert b"Sensitive pregnancy care" not in response.data
        assert b"Pregnancy" not in response.data
        assert b"Active patients" in response.data
        db.drop_all()


def test_global_search_returns_compact_results_without_clinical_data():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("reception-global@example.com", "01030100010", "Reception")
        patient = create_patient(66)
        db.session.add(Journey(patient_id=patient.id, journey_type="pregnancy", status="active", title="Private pregnancy", start_date=date.today()))
        db.session.commit()

        with app.test_client() as client:
            login(client, "reception-global@example.com")
            response = client.get("/patients/global-search?q=Patient+66")

        assert response.status_code == 200
        assert b"Patient 66" in response.data
        assert b"MRN" in response.data
        assert b"Private pregnancy" not in response.data
        assert b"patient-global-result" in response.data
        db.drop_all()


def test_drawer_has_search_sort_and_exact_record_links():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-links@example.com", "01030100011", "Doctor")
        patient = create_patient(67)
        visit = Visit(patient_id=patient.id, visit_type="general", status="completed", visit_date=datetime.now(timezone.utc))
        journey = Journey(patient_id=patient.id, journey_type="gynecology", status="active", title="Gyne care", start_date=date.today())
        appointment = Appointment(patient_id=patient.id, appointment_date=date.today() + timedelta(days=2), appointment_type="follow_up", status="booked", source="clinic")
        db.session.add_all([visit, journey, appointment])
        db.session.commit()

        with app.test_client() as client:
            login(client, "doctor-links@example.com")
            response = client.get("/patients/quick-list?journey=gynecology&sort=nearest&q=Patient+67")

        html = response.get_data(as_text=True)
        assert response.status_code == 200
        assert 'id="patient-drawer-search-input"' in html
        assert 'value="nearest" selected' in html
        assert f'/journeys/{journey.uuid}' in html
        assert f'/visits/{visit.uuid}' in html
        assert f'/appointments/{appointment.uuid}' in html
        assert "Why shown here" not in html
        db.drop_all()


def test_pending_review_badge_deep_links_and_reception_cannot_see_it():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        doctor = create_user("doctor-review-link@example.com", "01030100012", "Doctor")
        create_user("reception-review-link@example.com", "01030100013", "Reception")
        patient = create_patient(68)
        test = InvestigationTest(code="LINK-CBC", name_en="CBC", result_kind="text")
        db.session.add(test)
        db.session.flush()
        db.session.add(InvestigationResult(patient_id=patient.id, test_id=test.id, result_date=date.today(), result_text="Ready", status="entered", abnormal_flag="unknown", entered_by_user_id=doctor.id))
        db.session.commit()

        with app.test_client() as client:
            login(client, "doctor-review-link@example.com")
            doctor_response = client.get("/patients/quick-list?cohort=attention")
        g.pop("_login_user", None)
        with app.test_client() as client:
            login(client, "reception-review-link@example.com")
            reception_response = client.get("/patients/quick-list?cohort=active")

        assert f'/investigations/patients/{patient.uuid}' in doctor_response.get_data(as_text=True)
        assert b"pending review" in doctor_response.data
        assert b"attention-clinical patient-action-badge" not in reception_response.data
        db.drop_all()


def test_switchable_analytics_are_period_aware_and_permission_aware():
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        create_user("doctor-analytics@example.com", "01030100014", "Doctor")
        create_user("reception-analytics@example.com", "01030100015", "Reception")
        create_patient(69)

        with app.test_client() as client:
            login(client, "reception-analytics@example.com")
            reception_response = client.get("/patients/?period=30d")
        g.pop("_login_user", None)
        with app.test_client() as client:
            login(client, "doctor-analytics@example.com")
            doctor_response = client.get("/patients/?period=12m")

        assert b"Patient intelligence" in doctor_response.data
        assert b"New vs returning" in doctor_response.data
        assert b"Age distribution" in doctor_response.data
        assert b"Active care journeys" in doctor_response.data
        assert b"Follow-up status" in doctor_response.data
        assert b"Patient balances" in doctor_response.data
        assert b"12 months" in doctor_response.data
        assert b"Active care journeys" not in reception_response.data
        assert b"Follow-up status" not in reception_response.data
        assert b"30 days" in reception_response.data
        db.drop_all()
