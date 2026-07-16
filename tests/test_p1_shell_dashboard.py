from app import create_app
from app.extensions import db
from app.models import Patient, User, Visit
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def create_user(
    email="p1-doctor@example.com",
    phone="01077770001",
    role="Doctor",
):
    user = User(
        email=email,
        phone=phone,
        name="P1 User",
    )
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role)

    return user


def login(client, email="p1-doctor@example.com"):
    return client.post(
        "/auth/login",
        data={
            "login_identifier": email,
            "password": "12345678",
        },
    )


def create_patient():
    patient = Patient(
        medical_file_number=1,
        name_ar="Trial Patient Arabic",
        name_en="Trial Patient",
        search_name="trial patient",
        phone_primary="01077770002",
    )
    db.session.add(patient)
    db.session.commit()
    return patient


def test_anonymous_login_page_renders():
    app = make_app()

    with app.app_context():
        db.create_all()

        response = app.test_client().get("/auth/login")

        assert response.status_code == 200
        assert b"Login to Clinic OS" in response.data

        db.drop_all()


def test_dashboard_has_no_development_text():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user()

        client = app.test_client()
        login(client)

        response = client.get("/")

        assert response.status_code == 200
        assert b"Clinic overview" in response.data
        assert b"Recent patients" in response.data
        assert b"Recent visits" in response.data
        assert b"Stage 1" not in response.data
        assert b"Sprint 1.1" not in response.data
        assert b"Coming later" not in response.data

        db.drop_all()


def test_visits_index_works():
    app = make_app()

    with app.app_context():
        db.create_all()
        create_user()

        patient = create_patient()
        visit = Visit(
            patient_id=patient.id,
            visit_type="gyn",
            status="open",
        )
        db.session.add(visit)
        db.session.commit()

        client = app.test_client()
        login(client)

        response = client.get("/visits/")

        assert response.status_code == 200
        assert b"Trial Patient" in response.data
        assert b"Open" in response.data

        db.drop_all()


def test_reception_dashboard_hides_clinical_links():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            email="p1-reception@example.com",
            phone="01077770003",
            role="Reception",
        )

        client = app.test_client()
        login(
            client,
            email="p1-reception@example.com",
        )

        response = client.get("/")

        assert response.status_code == 200
        assert b'href="/visits/"' not in response.data
        assert b'href="/surgeries/"' not in response.data
        assert b"Recent visits" not in response.data
        assert b"Open visits" not in response.data
        assert b'href="/finance/"' in response.data

        db.drop_all()


def test_reception_cannot_open_visits_index():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            email="p1-reception-route@example.com",
            phone="01077770004",
            role="Reception",
        )

        client = app.test_client()
        login(
            client,
            email="p1-reception-route@example.com",
        )

        response = client.get("/visits/")

        assert response.status_code == 403

        db.drop_all()
