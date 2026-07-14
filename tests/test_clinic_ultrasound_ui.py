from datetime import date

from app import create_app
from app.extensions import db
from app.models import ClinicUltrasoundExam, User
from app.services.clinic_ultrasound_service import ClinicUltrasoundService
from app.services.patient_service import PatientService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService
from app.services.visit_service import VisitService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=False,
    )
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
        data={
            "login_identifier": email,
            "password": "12345678",
        },
        follow_redirects=True,
    )


def create_patient(phone="01088880400"):
    return PatientService.create_patient(
        name_ar="منى علي",
        name_en="Mona Ali",
        phone_primary=phone,
        date_of_birth=date(1996, 7, 1),
    )


def create_visit(patient, visit_type="obs"):
    return VisitService.create_visit(
        patient=patient,
        visit_type=visit_type,
        chief_complaint="Routine visit",
        plan="Visit plan remains outside ultrasound.",
    )


def ultrasound_post_data(**overrides):
    data = {
        "exam_type": ClinicUltrasoundExam.EXAM_TYPE_OBS,
        "exam_route": ClinicUltrasoundExam.ROUTE_TRANSABDOMINAL,
        "pregnancy_count": "Single",
        "viability": "Viable",
        "presentation": "Cephalic",
        "fetal_heart": "Seen",
        "fhr": "150",
        "placenta": "Fundal anterior",
        "liquor": "Average",
        "findings_text": "Single viable cephalic fetus.",
        "extra_note": "No obvious anomaly in this limited scan.",
        "impression": "Viable intrauterine pregnancy.",
        "sketch_note": "Placenta fundal anterior.",
    }
    data.update(overrides)
    return data


def test_doctor_sees_inline_ultrasound_form_without_exam_date_or_plan_field():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-us-inline@example.com", "01088880401", "Doctor")
        patient = create_patient()
        visit = create_visit(patient)

        client = app.test_client()
        login(client, "doctor-us-inline@example.com")

        response = client.get(f"/visits/{visit.uuid}")

        assert response.status_code == 200
        assert b"Clinic Ultrasound" in response.data
        assert b"Add Clinic Ultrasound" in response.data
        assert b"Save ultrasound" in response.data
        assert b'name="exam_date"' not in response.data
        assert b'name="plan"' not in response.data
        assert b"Extra note" in response.data
        assert b"Sketch note" in response.data

        db.drop_all()


def test_doctor_can_create_obs_ultrasound_inline_from_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-us-create@example.com", "01088880402", "Doctor")
        patient = create_patient(phone="01088880412")
        visit = create_visit(patient)

        client = app.test_client()
        login(client, "doctor-us-create@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/ultrasounds",
            data=ultrasound_post_data(),
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Ultrasound saved" in response.data
        assert b"Cephalic" in response.data
        assert b"Viable intrauterine pregnancy" in response.data

        exam = ClinicUltrasoundExam.query.filter_by(visit_id=visit.id).first()
        assert exam is not None
        assert exam.patient_id == patient.id
        assert exam.visit_id == visit.id
        assert exam.created_by_user_id == doctor.id
        assert exam.findings_json["presentation"] == "Cephalic"
        assert exam.exam_date == visit.visit_date

        db.drop_all()


def test_doctor_can_create_oi_ti_ultrasound_inline_from_visit():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        create_user("doctor-us-oiti@example.com", "01088880403", "Doctor")
        patient = create_patient(phone="01088880413")
        visit = create_visit(patient, visit_type="oiti")

        client = app.test_client()
        login(client, "doctor-us-oiti@example.com")

        response = client.post(
            f"/visits/{visit.uuid}/ultrasounds",
            data=ultrasound_post_data(
                exam_type=ClinicUltrasoundExam.EXAM_TYPE_OI_TI,
                exam_route=ClinicUltrasoundExam.ROUTE_TRANSVAGINAL,
                cycle_day="12",
                right_follicle_sizes="18, 16, 14",
                left_follicle_sizes="12, 10",
                endometrium_thickness_oi="8.5 mm",
                endometrium_pattern="Triple line",
                findings_text="Dominant follicle right ovary.",
                impression="Dominant follicle 18 mm.",
            ),
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Ultrasound saved" in response.data
        assert b"18, 16, 14" in response.data

        exam = ClinicUltrasoundExam.query.filter_by(visit_id=visit.id).first()
        assert exam.exam_type == ClinicUltrasoundExam.EXAM_TYPE_OI_TI
        assert exam.findings_json["cycle_day"] == "12"
        assert exam.findings_json["right_follicle_sizes"] == "18, 16, 14"

        db.drop_all()


def test_doctor_can_edit_ultrasound_inline_from_visit_card():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-us-edit@example.com", "01088880404", "Doctor")
        patient = create_patient(phone="01088880414")
        visit = create_visit(patient)

        exam = ClinicUltrasoundService.create_exam(
            visit=visit,
            exam_type=ClinicUltrasoundExam.EXAM_TYPE_OBS,
            exam_route=ClinicUltrasoundExam.ROUTE_TRANSABDOMINAL,
            findings_json={"presentation": "Breech"},
            findings_text="Initial findings.",
            impression="Initial impression.",
            actor_user=doctor,
        )

        client = app.test_client()
        login(client, "doctor-us-edit@example.com")

        edit_view = client.get(f"/visits/{visit.uuid}?edit_ultrasound={exam.uuid}")
        assert edit_view.status_code == 200
        assert b"Save changes" in edit_view.data

        response = client.post(
            f"/ultrasounds/{exam.uuid}/edit",
            data=ultrasound_post_data(
                presentation="Cephalic",
                findings_text="Updated findings.",
                impression="Updated impression.",
            ),
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Ultrasound updated" in response.data
        assert b"Updated impression" in response.data

        updated = db.session.get(ClinicUltrasoundExam, exam.id)
        assert updated.findings_json["presentation"] == "Cephalic"
        assert updated.findings_text == "Updated findings."

        db.drop_all()


def test_doctor_can_archive_ultrasound_inline():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-us-archive@example.com", "01088880405", "Doctor")
        patient = create_patient(phone="01088880415")
        visit = create_visit(patient)

        exam = ClinicUltrasoundService.create_exam(
            visit=visit,
            exam_type=ClinicUltrasoundExam.EXAM_TYPE_GYNE,
            exam_route=ClinicUltrasoundExam.ROUTE_TRANSVAGINAL,
            findings_json={"uterus_note": "Normal size"},
            impression="Normal pelvic scan.",
            actor_user=doctor,
        )

        client = app.test_client()
        login(client, "doctor-us-archive@example.com")

        response = client.post(
            f"/ultrasounds/{exam.uuid}/archive",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Ultrasound archived" in response.data

        archived = db.session.get(ClinicUltrasoundExam, exam.id)
        assert archived.is_active is False

        db.drop_all()


def test_patient_workspace_shows_recent_clinic_ultrasound_summary():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-us-workspace@example.com", "01088880406", "Doctor")
        patient = create_patient(phone="01088880416")
        visit = create_visit(patient)

        ClinicUltrasoundService.create_exam(
            visit=visit,
            exam_type=ClinicUltrasoundExam.EXAM_TYPE_OBS,
            exam_route=ClinicUltrasoundExam.ROUTE_TRANSABDOMINAL,
            findings_json={"presentation": "Cephalic"},
            impression="Workspace visible scan.",
            actor_user=doctor,
        )

        client = app.test_client()
        login(client, "doctor-us-workspace@example.com")

        response = client.get(f"/patients/{patient.uuid}")

        assert response.status_code == 200
        assert b"Clinic Ultrasounds" in response.data
        assert b"Workspace visible scan" in response.data

        db.drop_all()


def test_reception_is_blocked_from_ultrasound_manage_routes():
    app = make_app()

    with app.app_context():
        db.create_all()
        SettingsService.seed_defaults()

        doctor = create_user("doctor-us-owner@example.com", "01088880407", "Doctor")
        create_user("reception-us-blocked@example.com", "01088880408", "Reception")
        patient = create_patient(phone="01088880417")
        visit = create_visit(patient)

        exam = ClinicUltrasoundService.create_exam(
            visit=visit,
            exam_type=ClinicUltrasoundExam.EXAM_TYPE_OTHER,
            exam_route=ClinicUltrasoundExam.ROUTE_UNKNOWN,
            findings_text="Other ultrasound.",
            actor_user=doctor,
        )

        client = app.test_client()
        login(client, "reception-us-blocked@example.com")

        create_response = client.post(
            f"/visits/{visit.uuid}/ultrasounds",
            data=ultrasound_post_data(),
        )
        edit_response = client.post(
            f"/ultrasounds/{exam.uuid}/edit",
            data=ultrasound_post_data(),
        )
        archive_response = client.post(f"/ultrasounds/{exam.uuid}/archive")

        assert create_response.status_code == 403
        assert edit_response.status_code == 403
        assert archive_response.status_code == 403

        db.drop_all()
