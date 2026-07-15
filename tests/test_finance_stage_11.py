from datetime import date, datetime, timezone

from app import create_app
from app.extensions import db
from app.models import FinanceCharge, FinanceExpense, FinancePayment, Patient, User
from app.models.appointment import Appointment
from app.models.surgery import SurgeryCase
from app.services.appointment_service import AppointmentService
from app.services.finance_service import FinanceService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.surgery_service import SurgeryService
from app.services.visit_service import VisitService


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


def create_patient(phone="01077000000"):
    return PatientService.create_patient(
        name_ar="منى علي",
        name_en="Mona Ali",
        phone_primary=phone,
        date_of_birth=date(1994, 1, 1),
    )


def login(client, email):
    return client.post(
        "/auth/login",
        data={"login_identifier": email, "password": "12345678"},
        follow_redirects=True,
    )


def setup_context(role="Doctor", email="doctor-finance@example.com", phone="01077000001"):
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        user = create_user(email, phone, role)
        patient = create_patient()
        yield app, user, patient
        db.drop_all()


def test_appointment_embedded_finance_creates_charge_and_payment():
    for app, doctor, patient in setup_context():
        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_NEW_CONSULTATION,
            fee_amount="300",
            paid_amount="300",
            payment_method=FinancePayment.METHOD_CASH,
            created_by_user_id=doctor.id,
        )

        charge = FinanceService.get_charge_for_source(FinanceCharge.SOURCE_APPOINTMENT, appointment.id)
        assert charge is not None
        assert charge.service_type == FinanceCharge.SERVICE_CONSULTATION
        assert charge.status == FinanceCharge.STATUS_PAID
        assert charge.paid_amount == 300
        assert charge.payments.count() == 1


def test_visit_procedure_embedded_finance_creates_charge():
    for app, doctor, patient in setup_context("Doctor", "doctor-finance-visit@example.com", "01077000002"):
        visit = VisitService.create_visit(
            patient=patient,
            visit_type="procedure",
            chief_complaint="IUD insertion",
            billing_service_type=FinanceCharge.SERVICE_PROCEDURE,
            fee_amount="700",
            paid_amount="300",
            payment_method=FinancePayment.METHOD_INSTAPAY,
        )

        charge = FinanceService.get_charge_for_source(FinanceCharge.SOURCE_VISIT, visit.id)
        assert charge is not None
        assert charge.service_type == FinanceCharge.SERVICE_PROCEDURE
        assert charge.status == FinanceCharge.STATUS_PARTIAL
        assert charge.remaining_amount == 400


def test_surgery_embedded_finance_uses_existing_fee_paid_fields():
    for app, doctor, patient in setup_context("Doctor", "doctor-finance-surgery@example.com", "01077000003"):
        surgery = SurgeryService.create_surgery(
            patient=patient,
            procedure_name="Diagnostic hysteroscopy",
            procedure_category=SurgeryCase.CATEGORY_HYSTEROSCOPY,
            scheduled_at=datetime.now(timezone.utc),
            priority=SurgeryCase.PRIORITY_ROUTINE,
            fee_amount="5000",
            paid_amount="2000",
            payment_method=FinancePayment.METHOD_CASH,
            actor_user=doctor,
        )

        charge = FinanceService.get_charge_for_source(FinanceCharge.SOURCE_SURGERY, surgery.id)
        assert charge is not None
        assert charge.service_type == FinanceCharge.SERVICE_SURGERY
        assert charge.status == FinanceCharge.STATUS_PARTIAL
        assert surgery.payment_status == FinanceCharge.STATUS_PARTIAL


def test_expense_creation_and_dashboard_summary():
    for app, doctor, patient in setup_context("Doctor", "doctor-finance-expense@example.com", "01077000004"):
        FinanceService.create_expense(
            expense_date=date.today(),
            category=FinanceExpense.CATEGORY_CONSUMABLES,
            title="Gloves",
            amount="250",
            payment_method=FinancePayment.METHOD_CASH,
            actor_user=doctor,
        )

        expenses = FinanceService.list_expenses()
        assert len(expenses) == 1
        assert expenses[0].category == FinanceExpense.CATEGORY_CONSUMABLES

        summary = FinanceService.get_dashboard_summary(date.today())
        assert summary["total_expenses"] == 250


def test_finance_routes_and_reception_permissions():
    for app, reception, patient in setup_context("Reception", "reception-finance@example.com", "01077000005"):
        client = app.test_client()
        login(client, "reception-finance@example.com")

        response = client.get("/finance/", follow_redirects=True)
        assert response.status_code == 200
        assert b"Finance" in response.data

        response = client.get("/finance/expenses/new", follow_redirects=True)
        assert response.status_code == 403
