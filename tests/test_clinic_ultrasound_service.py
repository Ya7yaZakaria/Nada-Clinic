from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import ClinicUltrasoundExam, Permission, User
from app.services.clinic_ultrasound_service import ClinicUltrasoundService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_patient(phone="01088880200"):
    return PatientService.create_patient(
        name_ar="منى علي",
        name_en="Mona Ali",
        phone_primary=phone,
        date_of_birth=date(1996, 7, 1),
    )


def create_user(email, phone, role_name):
    user = User(email=email, phone=phone, name=role_name)
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role_name)

    return user


def test_create_exam_derives_patient_and_date_from_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-ultrasound@example.com", "01088880201", "Doctor")
        patient = create_patient()
        visit = VisitService.create_visit(patient=patient, visit_type="oiti")

        exam = ClinicUltrasoundService.create_exam(
            visit=visit,
            exam_type=ClinicUltrasoundExam.EXAM_TYPE_OI_TI,
            exam_route=ClinicUltrasoundExam.ROUTE_TRANSVAGINAL,
            findings_json={
                "cycle_day": "12",
                "right_follicles": "18, 16, 14",
                "left_follicles": "12, 10",
            },
            findings_text="Dominant follicle right ovary.",
            extra_note="Left simple cyst noted.",
            impression="Dominant follicle 18 mm.",
            sketch_note="Left ovarian cyst lateral.",
            actor_user=doctor,
        )

        assert exam.id is not None
        assert exam.patient_id == patient.id
        assert exam.visit_id == visit.id
        assert exam.created_by_user_id == doctor.id
        assert exam.exam_date == visit.visit_date
        assert exam.findings_json["right_follicles"] == "18, 16, 14"

        db.drop_all()


def test_create_exam_rejects_invalid_type_and_route():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone="01088880202")
        visit = VisitService.create_visit(patient=patient, visit_type="gyn")

        with pytest.raises(ValueError, match="Invalid ultrasound exam type"):
            ClinicUltrasoundService.create_exam(
                visit=visit,
                exam_type="bad",
            )

        with pytest.raises(ValueError, match="Invalid ultrasound exam route"):
            ClinicUltrasoundService.create_exam(
                visit=visit,
                exam_type=ClinicUltrasoundExam.EXAM_TYPE_GYNE,
                exam_route="bad",
            )

        db.drop_all()


def test_list_visit_exams_and_archive_exam():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        patient = create_patient(phone="01088880203")
        visit = VisitService.create_visit(patient=patient, visit_type="obs")

        exam = ClinicUltrasoundService.create_exam(
            visit=visit,
            exam_type=ClinicUltrasoundExam.EXAM_TYPE_OBS,
            exam_route=ClinicUltrasoundExam.ROUTE_TRANSABDOMINAL,
        )

        assert exam in ClinicUltrasoundService.list_visit_exams(visit)

        ClinicUltrasoundService.archive_exam(exam)

        assert exam not in ClinicUltrasoundService.list_visit_exams(visit)
        assert exam in ClinicUltrasoundService.list_visit_exams(visit, include_inactive=True)

        db.drop_all()


def test_seed_ultrasound_permissions_for_admin_doctor_only():
    app = make_app()

    with app.app_context():
        db.create_all()
        RBACService.seed_roles_permissions()

        assert Permission.query.filter_by(name="ultrasound.view").first() is not None
        assert Permission.query.filter_by(name="ultrasound.manage").first() is not None

        admin = create_user("admin-ultrasound@example.com", "01088880204", "Admin")
        doctor = create_user("doctor-ultrasound-rbac@example.com", "01088880205", "Doctor")
        reception = create_user("reception-ultrasound@example.com", "01088880206", "Reception")

        assert RBACService.user_has_permission(admin, "ultrasound.view")
        assert RBACService.user_has_permission(admin, "ultrasound.manage")
        assert RBACService.user_has_permission(doctor, "ultrasound.view")
        assert RBACService.user_has_permission(doctor, "ultrasound.manage")
        assert not RBACService.user_has_permission(reception, "ultrasound.view")
        assert not RBACService.user_has_permission(reception, "ultrasound.manage")

        db.drop_all()
