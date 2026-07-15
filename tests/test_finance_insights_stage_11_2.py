from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models import FinanceCharge, FinanceExpense, FinancePayment, User
from app.services.finance_service import FinanceService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost", WTF_CSRF_ENABLED=False)
    return app


def create_user(email, phone, role_name):
    user = User(email=email, phone=phone, name=role_name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()
    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)
    return user


def create_patient(phone="01088000000"):
    return PatientService.create_patient(
        name_ar="سارة أحمد",
        name_en="Sara Ahmed",
        phone_primary=phone,
        date_of_birth=date(1992, 1, 1),
    )


def login(client, email):
    return client.post(
        "/auth/login",
        data={"login_identifier": email, "password": "12345678"},
        follow_redirects=True,
    )


def setup_context(role="Doctor", email="doctor-finance-insights@example.com", phone="01088000001"):
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        user = create_user(email, phone, role)
        patient = create_patient()
        yield app, user, patient
        db.drop_all()


def test_finance_insights_summary_groups_revenue_expenses_and_payment_methods():
    for app, doctor, patient in setup_context():
        today = date.today()
        yesterday = today - timedelta(days=1)

        FinanceService.create_or_update_source_charge(
            patient=patient,
            source_type=FinanceCharge.SOURCE_APPOINTMENT,
            source_id=9001,
            service_type=FinanceCharge.SERVICE_CONSULTATION,
            title="كشف",
            gross_amount="300",
            paid_amount="300",
            payment_method=FinancePayment.METHOD_CASH,
            service_date=today,
            actor_user=doctor,
        )
        FinanceService.create_or_update_source_charge(
            patient=patient,
            source_type=FinanceCharge.SOURCE_VISIT,
            source_id=9002,
            service_type=FinanceCharge.SERVICE_PROCEDURE,
            title="Procedure",
            gross_amount="700",
            paid_amount="300",
            payment_method=FinancePayment.METHOD_INSTAPAY,
            service_date=yesterday,
            actor_user=doctor,
        )
        FinanceService.create_expense(
            expense_date=today,
            category=FinanceExpense.CATEGORY_CONSUMABLES,
            title="Gloves",
            amount="100",
            payment_method=FinancePayment.METHOD_CASH,
            actor_user=doctor,
        )

        summary = FinanceService.get_insights_summary(date_from=yesterday, date_to=today)

        assert summary["total_charges"] == 1000
        assert summary["total_collected"] == 600
        assert summary["total_remaining"] == 400
        assert summary["total_expenses"] == 100
        assert summary["net_profit"] == 500

        service_rows = {row["key"]: row for row in summary["service_breakdown"]}
        assert service_rows[FinanceCharge.SERVICE_CONSULTATION]["paid"] == 300
        assert service_rows[FinanceCharge.SERVICE_PROCEDURE]["remaining"] == 400

        method_rows = {row["key"]: row for row in summary["payment_method_breakdown"]}
        assert method_rows[FinancePayment.METHOD_CASH]["amount"] == 300
        assert method_rows[FinancePayment.METHOD_INSTAPAY]["amount"] == 300

        expense_rows = {row["key"]: row for row in summary["expense_category_breakdown"]}
        assert expense_rows[FinanceExpense.CATEGORY_CONSUMABLES]["amount"] == 100

        assert len(summary["daily_rows"]) == 2
        assert len(summary["outstanding_charges"]) == 1


def test_finance_insights_route_access_and_content():
    for app, doctor, patient in setup_context("Doctor", "doctor-finance-insights-ui@example.com", "01088000002"):
        FinanceService.create_or_update_source_charge(
            patient=patient,
            source_type=FinanceCharge.SOURCE_APPOINTMENT,
            source_id=9101,
            service_type=FinanceCharge.SERVICE_EMERGENCY,
            title="كشف طوارئ",
            gross_amount="500",
            paid_amount="500",
            payment_method=FinancePayment.METHOD_CASH,
            service_date=date.today(),
            actor_user=doctor,
        )

        client = app.test_client()
        login(client, "doctor-finance-insights-ui@example.com")

        response = client.get("/finance/insights", follow_redirects=True)

        assert response.status_code == 200
        assert b"Finance Insights" in response.data
        assert b"Revenue by service type" in response.data
        assert b"Payment methods" in response.data
        assert b"Outstanding balances" in response.data


def test_reception_cannot_open_finance_insights():
    for app, reception, patient in setup_context("Reception", "reception-finance-insights@example.com", "01088000003"):
        client = app.test_client()
        login(client, "reception-finance-insights@example.com")

        response = client.get("/finance/insights", follow_redirects=True)

        assert response.status_code == 403
