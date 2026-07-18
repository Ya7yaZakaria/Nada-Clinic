from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models import Appointment, FinanceCharge, FinancePayment, Patient, User, Visit
from app.services.dashboard_service import DashboardService
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def patient(number=1):
    record = Patient(medical_file_number=number, name_ar="مريضة", name_en=f"Patient {number}", search_name=f"patient {number}", gender="female", phone_primary=f"0100000{number:04d}")
    db.session.add(record)
    db.session.flush()
    return record


def user_with_role(role, email):
    user = User(email=email, phone="01099999999", name=f"{role} User")
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()
    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role)
    return user


def login(client, email):
    return client.post("/auth/login", data={"login_identifier": email, "password": "12345678"})


def test_empty_database_summaries_are_safe():
    app = make_app()
    with app.app_context():
        db.create_all()
        today = date.today()
        assert DashboardService.get_visit_summary(today, today)["total"] == 0
        appointments = DashboardService.get_appointment_summary(today, today)
        assert appointments["completion_rate"] == 0.0
        assert DashboardService.get_revenue_by_service(today, today)["values"] == [0.0] * 8
        assert DashboardService.get_ultrasound_summary(today, today)["clinic_exams"] == 0
        assert DashboardService.get_surgery_summary(today, today)["total"] == 0
        db.drop_all()


def test_visit_and_appointment_intelligence_and_upcoming_order():
    app = make_app()
    with app.app_context():
        db.create_all()
        person = patient()
        now = datetime.now(timezone.utc)
        db.session.add_all([
            Visit(patient_id=person.id, visit_type="obs", status="completed", visit_date=now),
            Visit(patient_id=person.id, visit_type="obs", status="open", visit_date=now),
            Visit(patient_id=person.id, visit_type="gyn", status="incomplete", visit_date=now),
            Appointment(patient_id=person.id, appointment_date=date.today(), appointment_time=time(23, 55), appointment_type=Appointment.TYPE_FOLLOW_UP, source=Appointment.SOURCE_PHONE, status=Appointment.STATUS_COMPLETED),
            Appointment(patient_id=person.id, appointment_date=date.today(), appointment_time=time(23, 56), appointment_type=Appointment.TYPE_EMERGENCY, source=Appointment.SOURCE_WHATSAPP, status=Appointment.STATUS_NO_SHOW),
            Appointment(patient_id=person.id, appointment_date=date.today(), appointment_time=time(23, 57), appointment_type=Appointment.TYPE_NEW_CONSULTATION, source=Appointment.SOURCE_CLINIC, status=Appointment.STATUS_CANCELLED),
            Appointment(patient_id=person.id, appointment_date=date.today() + timedelta(days=1), appointment_time=None, appointment_type=Appointment.TYPE_FOLLOW_UP, source=Appointment.SOURCE_CLINIC, status=Appointment.STATUS_BOOKED),
            Appointment(patient_id=person.id, appointment_date=date.today() + timedelta(days=1), appointment_time=time(9), appointment_type=Appointment.TYPE_FOLLOW_UP, source=Appointment.SOURCE_CLINIC, status=Appointment.STATUS_BOOKED),
        ])
        db.session.commit()
        visits = DashboardService.get_visit_summary(date.today(), date.today())
        assert (visits["total"], visits["completed"], visits["incomplete"], visits["open"]) == (3, 1, 1, 1)
        assert visits["most_common"] == "Obstetrics"
        summary = DashboardService.get_appointment_summary(date.today(), date.today())
        assert (
            summary["completed"],
            summary["no_show"],
            summary["cancelled"],
        ) == (1, 1, 1)
        assert (
            summary["completion_rate"],
            summary["no_show_rate"],
            summary["cancellation_rate"],
        ) == (33.3, 33.3, 33.3)
        upcoming = DashboardService.get_upcoming_appointments()
        assert upcoming[0].appointment_time == time(9)
        assert upcoming[1].appointment_time is None
        db.drop_all()


def test_revenue_by_service_uses_allocated_payments_only():
    app = make_app()
    with app.app_context():
        db.create_all()
        person = patient()
        charge = FinanceCharge(patient_id=person.id, source_type=FinanceCharge.SOURCE_MANUAL, service_type=FinanceCharge.SERVICE_SURGERY, title="Surgery", gross_amount=Decimal("1000"), net_amount=Decimal("1000"), paid_amount=Decimal("900"), remaining_amount=Decimal("100"), service_date=date.today())
        db.session.add(charge)
        db.session.flush()
        db.session.add_all([
            FinancePayment(patient_id=person.id, charge_id=charge.id, payment_date=date.today(), amount=Decimal("250"), payment_method=FinancePayment.METHOD_CASH),
            FinancePayment(patient_id=person.id, charge_id=None, payment_date=date.today(), amount=Decimal("75"), payment_method=FinancePayment.METHOD_CASH),
        ])
        db.session.commit()
        result = DashboardService.get_revenue_by_service(date.today(), date.today())
        assert result["values"][result["labels"].index("Surgery")] == 250.0
        assert sum(result["values"]) == 250.0
        db.drop_all()


def test_reception_never_calls_restricted_helpers(monkeypatch):
    app = make_app()
    restricted = (
        "get_visit_summary", "get_investigation_summary", "get_ultrasound_summary",
        "get_surgery_summary", "get_upcoming_surgeries", "get_module_activity",
        "get_revenue_by_service", "get_finance_summary",
    )
    def forbidden(*args, **kwargs):
        raise AssertionError("Reception called a restricted dashboard helper")
    for name in restricted:
        monkeypatch.setattr(DashboardService, name, forbidden)
    with app.app_context():
        db.create_all()
        user_with_role("Reception", "p23b-reception@example.com")
        client = app.test_client()
        login(client, "p23b-reception@example.com")
        response = client.get("/?preset=today")
        assert response.status_code == 200
        for marker in (b"Visits by Type", b"Investigation", b"Clinic Exam Mix", b"Scheduled-period Status", b"Collected by Service"):
            assert marker not in response.data
        db.drop_all()


def test_needs_attention_omits_zero_values():
    items = DashboardService.build_needs_attention(
        appointment_summary={
            "no_show": 0,
        },
        investigation_summary={
            "critical": 2,
            "awaiting_review": 0,
            "urgent_pending": 1,
        },
        ultrasound_summary={
            "external_pending": 0,
        },
        surgery_summary={
            "postponed": 0,
        },
        finance_summary={
            "outstanding": Decimal("0"),
        },
    )

    assert len(items) == 2
    assert {
        item["label"]
        for item in items
    } == {
        "Critical investigation results",
        "Urgent pending investigations",
    }


def test_finance_attention_is_marked_as_money():
    items = DashboardService.build_needs_attention(
        finance_summary={
            "outstanding": Decimal("1250.00"),
        },
    )

    assert len(items) == 1
    assert items[0]["endpoint"] == "finance.insights"
    assert items[0]["is_money"] is True


def test_reception_chart_payload_omits_restricted_keys(
    monkeypatch,
):
    app = make_app()

    restricted = (
        "get_visit_summary",
        "get_investigation_summary",
        "get_ultrasound_summary",
        "get_surgery_summary",
        "get_upcoming_surgeries",
        "get_module_activity",
        "get_revenue_by_service",
        "get_finance_summary",
    )

    def forbidden(*args, **kwargs):
        raise AssertionError(
            "Reception called a restricted "
            "dashboard helper"
        )

    for name in restricted:
        monkeypatch.setattr(
            DashboardService,
            name,
            forbidden,
        )

    with app.app_context():
        db.create_all()

        user_with_role(
            "Reception",
            "p23b-reception-json@example.com",
        )

        client = app.test_client()

        login(
            client,
            "p23b-reception-json@example.com",
        )

        response = client.get("/?preset=today")

        assert response.status_code == 200

        restricted_keys = (
            b'"visit_types"',
            b'"revenue_services"',
            b'"ultrasound_types"',
            b'"surgery_statuses"',
        )

        for key in restricted_keys:
            assert key not in response.data

        db.drop_all()
