from datetime import date, datetime, time, timezone, timedelta

from app import create_app
from app.extensions import db
from app.models import Patient, User, Visit
from app.models.surgery import SurgeryCase
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.surgery_analytics_service import SurgeryAnalyticsService
from app.services.surgery_service import SurgeryService
from app.services.timeline_service import TimelineService
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


def login(client, email):
    return client.post(
        "/auth/login",
        data={"login_identifier": email, "password": "12345678"},
        follow_redirects=True,
    )


def create_patient(phone="01099000000"):
    return PatientService.create_patient(
        name_ar="منى علي",
        name_en="Mona Ali",
        phone_primary=phone,
        date_of_birth=date(1996, 7, 1),
    )


def create_visit(patient):
    return VisitService.create_visit(
        patient=patient,
        visit_type="gyn",
        chief_complaint="AUB",
        plan="May need hysteroscopy, but this is not a SurgeryCase yet.",
    )


def setup_context(email="doctor-surgery@example.com", phone="01099000001", role="Doctor"):
    app = make_app()
    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        user = create_user(email, phone, role)
        patient = create_patient()
        visit = create_visit(patient)
        yield app, user, patient, visit
        db.drop_all()


def scheduled_time(days=2):
    return datetime.now(timezone.utc).replace(second=0, microsecond=0) + timedelta(days=days)


def test_surgery_service_create_complete_cancel_postpone_and_timeline():
    for app, doctor, patient, visit in setup_context():
        surgery = SurgeryService.create_surgery(
            patient=patient,
            source_visit=visit,
            procedure_name="Diagnostic hysteroscopy",
            procedure_category=SurgeryCase.CATEGORY_HYSTEROSCOPY,
            scheduled_at=scheduled_time(),
            priority=SurgeryCase.PRIORITY_ROUTINE,
            actor_user=doctor,
            fee_amount="5000",
            paid_amount="1000",
            payment_status=SurgeryCase.PAYMENT_PARTIAL,
        )

        assert surgery.status == SurgeryCase.STATUS_SCHEDULED
        assert surgery.patient_id == patient.id
        assert surgery.source_visit_id == visit.id

        events = TimelineService.get_patient_timeline(patient)
        assert any(event["source"] == "surgery" and event["source_uuid"] == surgery.uuid for event in events)

        SurgeryService.postpone_surgery(
            surgery,
            new_scheduled_at=scheduled_time(days=5),
            postponed_reason="Hospital timing changed.",
            actor_user=doctor,
        )
        assert surgery.status == SurgeryCase.STATUS_POSTPONED

        SurgeryService.complete_surgery(
            surgery,
            completed_at=scheduled_time(days=5),
            operative_findings="Small endometrial polyp.",
            operative_details="Diagnostic hysteroscopy and polypectomy.",
            complications="None",
            post_op_plan="Follow-up after 1 week.",
            actor_user=doctor,
        )
        assert surgery.status == SurgeryCase.STATUS_COMPLETED
        assert surgery.completed_by_user_id == doctor.id

        another = SurgeryService.create_surgery(
            patient=patient,
            procedure_name="D&C",
            procedure_category=SurgeryCase.CATEGORY_D_AND_C,
            scheduled_at=scheduled_time(days=7),
            priority=SurgeryCase.PRIORITY_ROUTINE,
            actor_user=doctor,
        )
        SurgeryService.cancel_surgery(another, cancel_reason="Patient cancelled.", actor_user=doctor)
        assert another.status == SurgeryCase.STATUS_CANCELLED


def test_surgery_analytics_counts_and_money():
    for app, doctor, patient, visit in setup_context("doctor-surgery-analytics@example.com", "01099000002"):
        SurgeryService.create_surgery(
            patient=patient,
            procedure_name="CS",
            procedure_category=SurgeryCase.CATEGORY_CESAREAN_SECTION,
            scheduled_at=scheduled_time(),
            priority=SurgeryCase.PRIORITY_ROUTINE,
            actor_user=doctor,
            fee_amount="10000",
            paid_amount="7000",
            payment_status=SurgeryCase.PAYMENT_PARTIAL,
        )
        surgery = SurgeryService.create_surgery(
            patient=patient,
            procedure_name="Hysteroscopy",
            procedure_category=SurgeryCase.CATEGORY_HYSTEROSCOPY,
            scheduled_at=scheduled_time(days=3),
            priority=SurgeryCase.PRIORITY_ROUTINE,
            actor_user=doctor,
            fee_amount="5000",
            paid_amount="5000",
            payment_status=SurgeryCase.PAYMENT_PAID,
        )
        SurgeryService.complete_surgery(
            surgery,
            completed_at=scheduled_time(days=3),
            actor_user=doctor,
        )

        summary = SurgeryAnalyticsService.summarize(SurgeryService.list_by_date_range())
        assert summary["total_count"] == 2
        assert summary["by_category"][SurgeryCase.CATEGORY_CESAREAN_SECTION] == 1
        assert summary["by_status"][SurgeryCase.STATUS_COMPLETED] == 1
        assert summary["total_fee"] == 15000
        assert summary["total_paid"] == 12000
        assert summary["outstanding"] == 3000


def test_doctor_can_use_surgery_ui_and_reception_blocked():
    for app, doctor, patient, visit in setup_context("doctor-surgery-ui@example.com", "01099000003"):
        client = app.test_client()
        login(client, "doctor-surgery-ui@example.com")

        response = client.get("/surgeries", follow_redirects=True)
        assert response.status_code == 200
        assert b"Surgery Dashboard" in response.data

        response = client.post(
            f"/surgeries/visit/{visit.uuid}/new",
            data={
                "patient_id": patient.id,
                "procedure_name": "Diagnostic hysteroscopy",
                "procedure_category": SurgeryCase.CATEGORY_HYSTEROSCOPY,
                "scheduled_date": date.today().isoformat(),
                "scheduled_time": "10:00",
                "location": "Hospital X",
                "priority": SurgeryCase.PRIORITY_ROUTINE,
                "pre_op_note": "CBC and consent before procedure.",
                "surgery_note": "",
                "fee_amount": "5000",
                "paid_amount": "1000",
                "payment_status": SurgeryCase.PAYMENT_PARTIAL,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Surgery scheduled from visit" in response.data
        assert b"Diagnostic hysteroscopy" in response.data

        surgery = SurgeryCase.query.filter_by(patient_id=patient.id).first()
        assert surgery is not None
        assert surgery.source_visit_id == visit.id

        response = client.get(f"/patients/{patient.uuid}", follow_redirects=True)
        assert response.status_code == 200
        assert b"Surgical History" in response.data
        assert b"Diagnostic hysteroscopy" in response.data
        assert b"Surgery" in response.data

        response = client.post(
            f"/surgeries/{surgery.uuid}/complete",
            data={
                "completed_date": date.today().isoformat(),
                "completed_time": "11:00",
                "operative_findings": "Normal cavity.",
                "operative_details": "Diagnostic hysteroscopy.",
                "complications": "None",
                "post_op_plan": "Follow-up.",
                "fee_amount": "5000",
                "paid_amount": "5000",
                "payment_status": SurgeryCase.PAYMENT_PAID,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Surgery completed" in response.data
        assert SurgeryCase.query.first().status == SurgeryCase.STATUS_COMPLETED

    for app, reception, patient, visit in setup_context("reception-surgery-ui@example.com", "01099000004", "Reception"):
        client = app.test_client()
        login(client, "reception-surgery-ui@example.com")
        response = client.get("/surgeries", follow_redirects=True)
        assert response.status_code == 403
