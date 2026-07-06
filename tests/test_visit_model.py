from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Patient, User, Visit, VisitAuditLog
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_user(email, phone, role_name, name="Test User"):
    user = User(email=email, phone=phone, name=name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)

    return user


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


def test_visit_can_be_created_for_patient():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        visit = VisitService.create_visit(
            patient=patient,
            visit_type="gyn",
            chief_complaint="Pelvic pain",
            history="Pain for 3 days",
            examination="Stable",
            assessment="Likely simple cyst",
            plan="Follow up ultrasound",
        )

        assert visit.id is not None
        assert visit.uuid is not None
        assert visit.patient_id == patient.id
        assert visit.visit_type == "gyn"
        assert visit.status == "open"
        assert visit.is_locked is False
        assert visit.chief_complaint == "Pelvic pain"

        db.drop_all()


def test_visit_requires_patient():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        with pytest.raises(ValueError, match="Visit must belong to a patient"):
            VisitService.create_visit(visit_type="general")

        db.drop_all()


def test_visit_rejects_invalid_type():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        with pytest.raises(ValueError, match="Invalid visit type"):
            VisitService.create_visit(patient=patient, visit_type="invalid")

        db.drop_all()


def test_visit_rejects_invalid_status():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        with pytest.raises(ValueError, match="Invalid visit status"):
            VisitService.create_visit(
                patient=patient,
                visit_type="general",
                status="archived",
            )

        db.drop_all()


def test_visit_note_fields_can_be_updated_while_open():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = VisitService.create_visit(patient=patient, visit_type="general")

        VisitService.update_visit(
            visit,
            chief_complaint="Bleeding",
            history="Irregular bleeding",
            examination="No acute distress",
            assessment="AUB",
            plan="Labs and follow-up",
            follow_up_date=date(2026, 7, 20),
        )

        updated_visit = db.session.get(Visit, visit.id)

        assert updated_visit.chief_complaint == "Bleeding"
        assert updated_visit.history == "Irregular bleeding"
        assert updated_visit.examination == "No acute distress"
        assert updated_visit.assessment == "AUB"
        assert updated_visit.plan == "Labs and follow-up"
        assert updated_visit.follow_up_date == date(2026, 7, 20)

        db.drop_all()


def test_complete_visit_requires_confirmation():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        doctor = create_user("doctor@example.com", "01050000001", "Doctor", "Doctor User")
        visit = VisitService.create_visit(patient=patient, visit_type="general")

        with pytest.raises(ValueError, match="completion must be confirmed"):
            VisitService.complete_visit(visit, actor_user=doctor, confirmed=False)

        assert visit.status == "open"

        db.drop_all()


def test_complete_visit_locks_visit_and_creates_audit_log():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        doctor = create_user("doctor@example.com", "01050000002", "Doctor", "Doctor User")
        visit = VisitService.create_visit(patient=patient, visit_type="general")

        VisitService.complete_visit(visit, actor_user=doctor, confirmed=True)

        completed_visit = db.session.get(Visit, visit.id)
        audit_log = VisitAuditLog.query.filter_by(
            visit_id=visit.id,
            action="visit.completed",
        ).first()

        assert completed_visit.status == "completed"
        assert completed_visit.is_locked is True
        assert completed_visit.completed_at is not None
        assert completed_visit.completed_by_user_id == doctor.id
        assert audit_log is not None
        assert audit_log.from_status == "open"
        assert audit_log.to_status == "completed"
        assert audit_log.actor_user_id == doctor.id

        db.drop_all()


def test_locked_completed_visit_cannot_be_updated_before_reopen():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        doctor = create_user("doctor@example.com", "01050000003", "Doctor", "Doctor User")
        visit = VisitService.create_visit(patient=patient, visit_type="general")
        VisitService.complete_visit(visit, actor_user=doctor, confirmed=True)

        with pytest.raises(ValueError, match="Completed visit is locked"):
            VisitService.update_visit(visit, plan="Changed plan")

        db.drop_all()


def test_reopen_visit_requires_confirmation():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        doctor = create_user("doctor@example.com", "01050000004", "Doctor", "Doctor User")
        visit = VisitService.create_visit(patient=patient, visit_type="general")
        VisitService.complete_visit(visit, actor_user=doctor, confirmed=True)

        with pytest.raises(ValueError, match="reopen must be confirmed"):
            VisitService.reopen_visit(visit, actor_user=doctor, confirmed=False)

        assert visit.status == "completed"

        db.drop_all()


def test_reopen_visit_requires_doctor_or_admin():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        doctor = create_user("doctor@example.com", "01050000005", "Doctor", "Doctor User")
        reception = create_user("reception@example.com", "01050000006", "Reception", "Reception User")
        visit = VisitService.create_visit(patient=patient, visit_type="general")
        VisitService.complete_visit(visit, actor_user=doctor, confirmed=True)

        with pytest.raises(PermissionError, match="Only Doctor/Admin"):
            VisitService.reopen_visit(visit, actor_user=reception, confirmed=True)

        assert visit.status == "completed"

        db.drop_all()


def test_doctor_can_reopen_completed_visit_with_audit_log():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        doctor = create_user("doctor@example.com", "01050000007", "Doctor", "Doctor User")
        visit = VisitService.create_visit(patient=patient, visit_type="general")
        VisitService.complete_visit(visit, actor_user=doctor, confirmed=True)

        VisitService.reopen_visit(visit, actor_user=doctor, confirmed=True)

        reopened_visit = db.session.get(Visit, visit.id)
        audit_log = VisitAuditLog.query.filter_by(
            visit_id=visit.id,
            action="visit.reopened",
        ).first()

        assert reopened_visit.status == "open"
        assert reopened_visit.is_locked is False
        assert reopened_visit.reopened_at is not None
        assert reopened_visit.reopened_by_user_id == doctor.id
        assert audit_log is not None
        assert audit_log.from_status == "completed"
        assert audit_log.to_status == "open"
        assert audit_log.actor_user_id == doctor.id

        db.drop_all()


def test_admin_can_reopen_completed_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        doctor = create_user("doctor@example.com", "01050000008", "Doctor", "Doctor User")
        admin = create_user("admin@example.com", "01050000009", "Admin", "Admin User")
        visit = VisitService.create_visit(patient=patient, visit_type="general")
        VisitService.complete_visit(visit, actor_user=doctor, confirmed=True)

        VisitService.reopen_visit(visit, actor_user=admin, confirmed=True)

        assert visit.status == "open"
        assert visit.reopened_by_user_id == admin.id

        db.drop_all()


def test_patient_visits_and_last_visit_helpers():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()

        first_visit = VisitService.create_visit(patient=patient, visit_type="gyn")
        second_visit = VisitService.create_visit(patient=patient, visit_type="obs")

        visits = VisitService.get_patient_visits(patient)
        last_visit = VisitService.get_last_visit(patient)

        assert len(visits) == 2
        assert first_visit in visits
        assert second_visit in visits
        assert last_visit is not None

        db.drop_all()


def test_visit_is_unassigned_to_journey_in_sprint_3_1():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()
        patient = create_patient()
        visit = VisitService.create_visit(patient=patient, visit_type="general")

        assert VisitService.has_unassigned_journey(visit) is True
        assert not hasattr(visit, "journey_id")

        db.drop_all()


def test_visit_type_and_status_labels():
    assert VisitService.get_visit_type_label("obs") == "OBS"
    assert VisitService.get_visit_type_label("oiti") == "OITI"
    assert VisitService.get_status_label("completed") == "Completed"
