from app import create_app
from app.extensions import db
from app.models import User
from app.services.dashboard_service import (
    DashboardService,
)
from app.services.finance_service import (
    FinanceService,
)
from app.services.rbac_service import (
    RBACService,
)


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
    )
    return app


def create_user(
    email,
    phone,
    role,
):
    user = User(
        email=email,
        phone=phone,
        name=f"{role} Dashboard User",
    )

    user.set_password("12345678")

    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(
        user,
        role,
    )

    return user


def login(client, email):
    return client.post(
        "/auth/login",
        data={
            "login_identifier": email,
            "password": "12345678",
        },
    )


def test_dashboard_requires_login():
    app = make_app()

    with app.app_context():
        db.create_all()

        response = (
            app.test_client().get("/")
        )

        assert response.status_code == 302

        db.drop_all()


def test_doctor_dashboard_foundation():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "p23-doctor@example.com",
            "01090000001",
            "Doctor",
        )

        client = app.test_client()

        login(
            client,
            "p23-doctor@example.com",
        )

        response = client.get(
            "/?preset=this_month"
        )

        assert response.status_code == 200
        assert (
            b"Clinic Dashboard"
            in response.data
        )
        assert (
            b'id="dashboard-live-clock"'
            in response.data
        )
        assert (
            b'name="date_from"'
            in response.data
        )
        assert (
            b'name="date_to"'
            in response.data
        )
        assert (
            b"Activity Trend"
            in response.data
        )
        assert (
            b"Active Journeys"
            in response.data
        )
        assert (
            b"Revenue vs Expenses"
            in response.data
        )
        assert (
            b"Status Overview"
            in response.data
        )
        assert (
            b"Today Clinic"
            in response.data
        )
        assert (
            b"Open visits"
            not in response.data
        )
        assert (
            b"Open Visits"
            not in response.data
        )

        db.drop_all()


def test_reception_dashboard_hides_restricted_data():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "p23-reception@example.com",
            "01090000002",
            "Reception",
        )

        client = app.test_client()

        login(
            client,
            "p23-reception@example.com",
        )

        response = client.get(
            "/?preset=today"
        )

        assert response.status_code == 200
        assert (
            b"Active Journeys"
            not in response.data
        )
        assert (
            b"Revenue vs Expenses"
            not in response.data
        )
        assert (
            b"Net Income"
            not in response.data
        )
        assert (
            b'href="/visits/"'
            not in response.data
        )
        assert (
            b"Today Clinic"
            in response.data
        )

        db.drop_all()


def test_reversed_range_falls_back():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "p23-range@example.com",
            "01090000003",
            "Doctor",
        )

        client = app.test_client()

        login(
            client,
            "p23-range@example.com",
        )

        response = client.get(
            "/?date_from=2026-07-20"
            "&date_to=2026-07-01"
        )

        assert response.status_code == 200
        assert (
            b"Invalid date range"
            in response.data
        )
        assert (
            b"Showing this month instead"
            in response.data
        )

        db.drop_all()

def test_reception_dashboard_uses_permission_aware_queries(
    monkeypatch,
):
    app = make_app()

    captured = {}

    def fake_kpis(
        date_from,
        date_to,
        *,
        include_patients,
        include_visits,
        include_appointments,
    ):
        captured["kpis"] = {
            "patients": include_patients,
            "visits": include_visits,
            "appointments": include_appointments,
        }

        return {
            "active_patients": 0,
            "new_patients": 0,
            "visits": None,
            "appointments": 0,
        }

    def fake_activity(
        date_from,
        date_to,
        *,
        include_patients,
        include_visits,
        include_appointments,
    ):
        captured["activity"] = {
            "patients": include_patients,
            "visits": include_visits,
            "appointments": include_appointments,
        }

        return {
            "labels": ["17 Jul"],
            "new_patients": [0],
            "appointments": [0],
        }

    def forbidden_finance(*args, **kwargs):
        raise AssertionError(
            "Reception must not query finance insights."
        )

    monkeypatch.setattr(
        DashboardService,
        "get_clinic_kpis",
        fake_kpis,
    )
    monkeypatch.setattr(
        DashboardService,
        "get_activity_trend",
        fake_activity,
    )
    monkeypatch.setattr(
        FinanceService,
        "get_insights_summary",
        forbidden_finance,
    )

    with app.app_context():
        db.create_all()

        create_user(
            "p23-isolation@example.com",
            "01090000004",
            "Reception",
        )

        client = app.test_client()

        login(
            client,
            "p23-isolation@example.com",
        )

        response = client.get(
            "/?preset=today"
        )

        assert response.status_code == 200

        assert captured["kpis"] == {
            "patients": True,
            "visits": False,
            "appointments": True,
        }

        assert captured["activity"] == {
            "patients": True,
            "visits": False,
            "appointments": True,
        }

        assert b'"visits"' not in response.data
        assert (
            b"Revenue vs Expenses"
            not in response.data
        )

        db.drop_all()


def test_dashboard_service_omits_disallowed_activity_keys():
    app = make_app()

    with app.app_context():
        db.create_all()

        period = DashboardService.resolve_period(
            preset="today",
        )

        activity = (
            DashboardService.get_activity_trend(
                period["date_from"],
                period["date_to"],
                include_patients=True,
                include_visits=False,
                include_appointments=True,
            )
        )

        kpis = DashboardService.get_clinic_kpis(
            period["date_from"],
            period["date_to"],
            include_patients=True,
            include_visits=False,
            include_appointments=True,
        )

        assert "new_patients" in activity
        assert "appointments" in activity
        assert "visits" not in activity

        assert kpis["active_patients"] == 0
        assert kpis["new_patients"] == 0
        assert kpis["appointments"] == 0
        assert kpis["visits"] is None

        db.drop_all()
