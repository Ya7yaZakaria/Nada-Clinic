from datetime import date, timedelta
from decimal import Decimal
import json

from app import create_app
from app.extensions import db
from app.models import (
    Appointment,
    FinanceCharge,
    Patient,
    User,
    Visit,
)
from app.services.appointment_service import (
    AppointmentService,
)
from app.services.rbac_service import RBACService


def make_app():
    app = create_app("testing")
    app.config.update(
        SERVER_NAME="localhost",
    )
    return app


def create_user(role, email, phone):
    user = User(
        email=email,
        phone=phone,
        name=f"{role} User",
    )
    user.set_password("12345678")

    db.session.add(user)
    db.session.commit()

    RBACService.seed_roles_permissions()
    RBACService.assign_role(user, role)

    return user


def create_patient(number):
    patient = Patient(
        medical_file_number=number,
        name_ar="HTMX Patient",
        name_en="HTMX Patient",
        search_name="htmx patient",
        gender="female",
        phone_primary=f"010{number}",
    )

    db.session.add(patient)
    db.session.commit()

    return patient


def login(client, email):
    return client.post(
        "/auth/login",
        data={
            "login_identifier": email,
            "password": "12345678",
        },
    )


def test_today_clinic_renders_cancel_and_reschedule():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "htmx-actions@example.com",
            "01099000001",
        )

        patient = create_patient(99001)

        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=(
                Appointment.TYPE_FOLLOW_UP
            ),
        )

        client = app.test_client()
        login(client, "htmx-actions@example.com")

        response = client.get(
            f"/clinic/day/{date.today().isoformat()}"
        )

        assert response.status_code == 200
        assert b"/cancel/modal" in response.data
        assert b"/reschedule/modal" in response.data
        assert b"Cancel" in response.data
        assert b"Reschedule" in response.data
        assert (
            b"clinic-patient-cancel-action"
            in response.data
        )
        assert b"btn-danger" in response.data

        db.drop_all()


def test_cancel_modal_renders():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "htmx-cancel-modal@example.com",
            "01099000002",
        )

        patient = create_patient(99002)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        client = app.test_client()

        login(
            client,
            "htmx-cancel-modal@example.com",
        )

        response = client.get(
            f"/appointments/{appointment.uuid}"
            "/cancel/modal"
        )

        assert response.status_code == 200
        assert (
            b'id="clinic-action-modal-content"'
            in response.data
        )
        assert b"Cancel Appointment" in response.data
        assert b"Cancel reason" in response.data
        assert b"btn btn-danger" in response.data
        assert b">\n                        at\n" in response.data
        assert b"\n                    ?\n" not in response.data

        db.drop_all()


def test_cancel_requires_reason():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "htmx-cancel-invalid@example.com",
            "01099000003",
        )

        patient = create_patient(99003)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        client = app.test_client()

        login(
            client,
            "htmx-cancel-invalid@example.com",
        )

        response = client.post(
            f"/appointments/{appointment.uuid}/cancel",
            data={"reason": ""},
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 200
        assert (
            b'id="clinic-action-modal-content"'
            in response.data
        )
        assert b"This field is required." in response.data

        db.session.refresh(appointment)

        assert (
            appointment.status
            == Appointment.STATUS_BOOKED
        )

        db.drop_all()


def test_htmx_cancel_success():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "htmx-cancel-success@example.com",
            "01099000004",
        )

        patient = create_patient(99004)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        client = app.test_client()

        login(
            client,
            "htmx-cancel-success@example.com",
        )

        response = client.post(
            f"/appointments/{appointment.uuid}/cancel",
            data={"reason": "Patient requested"},
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 204

        trigger = json.loads(
            response.headers["HX-Trigger"]
        )

        assert "clinic:action-success" in trigger

        db.session.refresh(appointment)

        assert (
            appointment.status
            == Appointment.STATUS_CANCELLED
        )
        assert (
            appointment.cancel_reason
            == "Patient requested"
        )

        db.drop_all()


def test_reschedule_validation_stays_in_modal():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "htmx-reschedule-invalid@example.com",
            "01099000005",
        )

        patient = create_patient(99005)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        client = app.test_client()

        login(
            client,
            "htmx-reschedule-invalid@example.com",
        )

        response = client.post(
            f"/appointments/{appointment.uuid}/reschedule",
            data={
                "appointment_date": "",
                "appointment_time": "",
            },
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 200
        assert (
            b'id="clinic-action-modal-content"'
            in response.data
        )
        assert b"This field is required." in response.data

        db.session.refresh(appointment)

        assert (
            appointment.status
            == Appointment.STATUS_BOOKED
        )

        db.drop_all()


def test_htmx_reschedule_success():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "htmx-reschedule-success@example.com",
            "01099000006",
        )

        patient = create_patient(99006)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        destination_date = (
            date.today() + timedelta(days=1)
        )

        client = app.test_client()

        login(
            client,
            "htmx-reschedule-success@example.com",
        )

        response = client.post(
            f"/appointments/{appointment.uuid}/reschedule",
            data={
                "appointment_date": (
                    destination_date.isoformat()
                ),
                "appointment_time": "14:30",
            },
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 204

        trigger = json.loads(
            response.headers["HX-Trigger"]
        )

        assert "clinic:action-success" in trigger

        db.session.refresh(appointment)

        assert (
            appointment.status
            == Appointment.STATUS_RESCHEDULED
        )
        assert appointment.rescheduled_to is not None
        assert (
            appointment.rescheduled_to.appointment_date
            == destination_date
        )

        db.drop_all()


def test_cancel_and_reschedule_block_after_visit():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(99007)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        visit = Visit(
            patient_id=patient.id,
            appointment_id=appointment.id,
            visit_type="general",
            status="open",
        )

        db.session.add(visit)
        db.session.commit()

        try:
            AppointmentService.cancel_appointment(
                appointment,
                reason="Not allowed",
            )
        except ValueError as exc:
            assert "Visit has started" in str(exc)
        else:
            raise AssertionError(
                "Cancel should be blocked after Visit start."
            )

        try:
            AppointmentService.reschedule_appointment(
                appointment,
                new_date=(
                    date.today()
                    + timedelta(days=1)
                ),
            )
        except ValueError as exc:
            assert "Visit has started" in str(exc)
        else:
            raise AssertionError(
                "Reschedule should be blocked after Visit start."
            )

        db.drop_all()


def force_login(client, user):
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)
        session["_fresh"] = True


def test_reschedule_modal_renders():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "htmx-reschedule-modal@example.com",
            "01099000008",
        )

        patient = create_patient(99008)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        client = app.test_client()

        login(
            client,
            "htmx-reschedule-modal@example.com",
        )

        response = client.get(
            f"/appointments/{appointment.uuid}"
            "/reschedule/modal"
        )

        assert response.status_code == 200
        assert (
            b'id="clinic-action-modal-content"'
            in response.data
        )
        assert b"Reschedule Appointment" in response.data
        assert b"New appointment date" in response.data
        assert b"New appointment time" in response.data
        assert b"\n                    ?\n" not in response.data

        db.drop_all()


def test_freeze_normal_fallbacks_return_to_today_clinic():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "fallback-actions@example.com",
            "01099000009",
        )

        first_patient = create_patient(99009)
        second_patient = create_patient(99010)

        cancel_appointment = (
            AppointmentService.create_appointment(
                patient_id=first_patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        reschedule_appointment = (
            AppointmentService.create_appointment(
                patient_id=second_patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        client = app.test_client()

        login(
            client,
            "fallback-actions@example.com",
        )

        cancel_response = client.post(
            f"/appointments/{cancel_appointment.uuid}"
            "/cancel"
            "?resolved_filter=cancelled"
            "&resolved_sort=oldest",
            data={"reason": "Patient requested"},
            follow_redirects=False,
        )

        assert cancel_response.status_code == 302

        cancel_location = (
            cancel_response.headers["Location"]
        )

        assert (
            f"/clinic/day/{date.today().isoformat()}"
            in cancel_location
        )
        assert "resolved_filter=cancelled" in cancel_location
        assert "resolved_sort=oldest" in cancel_location

        destination_date = (
            date.today() + timedelta(days=1)
        )

        reschedule_response = client.post(
            f"/appointments/{reschedule_appointment.uuid}"
            "/reschedule"
            "?resolved_filter=rescheduled"
            "&resolved_sort=oldest",
            data={
                "appointment_date": (
                    destination_date.isoformat()
                ),
                "appointment_time": "13:15",
            },
            follow_redirects=False,
        )

        assert reschedule_response.status_code == 302

        reschedule_location = (
            reschedule_response.headers["Location"]
        )

        assert (
            f"/clinic/day/{date.today().isoformat()}"
            in reschedule_location
        )
        assert (
            "resolved_filter=rescheduled"
            in reschedule_location
        )
        assert (
            "resolved_sort=oldest"
            in reschedule_location
        )

        db.drop_all()


def test_doctor_is_blocked_from_cancel_and_reschedule():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Doctor",
            "doctor-actions-blocked@example.com",
            "01099000011",
        )

        patient = create_patient(99011)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        client = app.test_client()

        login(
            client,
            "doctor-actions-blocked@example.com",
        )

        responses = [
            client.get(
                f"/appointments/{appointment.uuid}"
                "/cancel/modal"
            ),
            client.get(
                f"/appointments/{appointment.uuid}"
                "/reschedule/modal"
            ),
            client.post(
                f"/appointments/{appointment.uuid}"
                "/cancel",
                data={"reason": "Not permitted"},
            ),
            client.post(
                f"/appointments/{appointment.uuid}"
                "/reschedule",
                data={
                    "appointment_date": (
                        date.today()
                        + timedelta(days=1)
                    ).isoformat(),
                    "appointment_time": "10:30",
                },
            ),
        ]

        assert all(
            response.status_code == 403
            for response in responses
        )

        db.session.refresh(appointment)

        assert (
            appointment.status
            == Appointment.STATUS_BOOKED
        )

        db.drop_all()


def test_cancel_and_reschedule_require_csrf_when_enabled():
    app = make_app()

    app.config.update(
        SERVER_NAME="localhost",
        WTF_CSRF_ENABLED=True,
    )

    with app.app_context():
        db.create_all()

        reception = create_user(
            "Reception",
            "csrf-actions@example.com",
            "01099000012",
        )

        patient = create_patient(99012)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        client = app.test_client()
        force_login(client, reception)

        cancel_response = client.post(
            f"/appointments/{appointment.uuid}/cancel",
            data={"reason": "Missing token"},
        )

        reschedule_response = client.post(
            f"/appointments/{appointment.uuid}"
            "/reschedule",
            data={
                "appointment_date": (
                    date.today()
                    + timedelta(days=1)
                ).isoformat(),
                "appointment_time": "11:45",
            },
        )

        assert cancel_response.status_code == 400
        assert reschedule_response.status_code == 400

        db.session.refresh(appointment)

        assert (
            appointment.status
            == Appointment.STATUS_BOOKED
        )

        db.drop_all()


def test_duplicate_reschedule_stays_in_modal():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "duplicate-reschedule@example.com",
            "01099000013",
        )

        patient = create_patient(99013)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        destination_date = (
            date.today() + timedelta(days=1)
        )

        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=destination_date,
            appointment_type=(
                Appointment.TYPE_FOLLOW_UP
            ),
        )

        client = app.test_client()

        login(
            client,
            "duplicate-reschedule@example.com",
        )

        response = client.post(
            f"/appointments/{appointment.uuid}"
            "/reschedule",
            data={
                "appointment_date": (
                    destination_date.isoformat()
                ),
                "appointment_time": "12:00",
            },
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 200
        assert (
            b'id="clinic-action-modal-content"'
            in response.data
        )

        db.session.refresh(appointment)

        assert (
            appointment.status
            == Appointment.STATUS_BOOKED
        )
        assert appointment.rescheduled_to is None

        db.drop_all()


def test_cancelled_appointment_cancels_unpaid_charge():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(99014)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        charge = FinanceCharge(
            patient_id=patient.id,
            source_type=(
                FinanceCharge.SOURCE_APPOINTMENT
            ),
            source_id=appointment.id,
            service_type=(
                FinanceCharge.SERVICE_FOLLOW_UP
            ),
            title="Follow-up",
            gross_amount=Decimal("300.00"),
            discount_amount=Decimal("0.00"),
            net_amount=Decimal("300.00"),
            paid_amount=Decimal("0.00"),
            remaining_amount=Decimal("300.00"),
            status=FinanceCharge.STATUS_UNPAID,
            service_date=date.today(),
        )

        db.session.add(charge)
        db.session.commit()

        AppointmentService.cancel_appointment(
            appointment,
            reason="Patient requested",
        )

        db.session.refresh(charge)

        assert (
            charge.status
            == FinanceCharge.STATUS_CANCELLED
        )
        assert (
            charge.remaining_amount
            == Decimal("0.00")
        )

        db.drop_all()


def test_resolved_appointment_rejects_repeat_actions():
    app = make_app()

    with app.app_context():
        db.create_all()

        patient = create_patient(99015)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        AppointmentService.cancel_appointment(
            appointment,
            reason="First cancellation",
        )

        operations = [
            lambda: AppointmentService.cancel_appointment(
                appointment,
                reason="Second cancellation",
            ),
            lambda: (
                AppointmentService.reschedule_appointment(
                    appointment,
                    new_date=(
                        date.today()
                        + timedelta(days=1)
                    ),
                )
            ),
        ]

        for operation in operations:
            try:
                operation()
            except ValueError as exc:
                assert "active appointment" in str(exc).lower()
            else:
                raise AssertionError(
                    "Resolved appointment action "
                    "should be rejected."
                )

        db.drop_all()


def test_visit_link_hides_operational_action_urls():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "visit-hidden-actions@example.com",
            "01099000016",
        )

        patient = create_patient(99016)

        appointment = (
            AppointmentService.create_appointment(
                patient_id=patient.id,
                appointment_date=date.today(),
                appointment_type=(
                    Appointment.TYPE_FOLLOW_UP
                ),
            )
        )

        visit = Visit(
            patient_id=patient.id,
            appointment_id=appointment.id,
            visit_type="general",
            status="open",
        )

        db.session.add(visit)
        db.session.commit()

        client = app.test_client()

        login(
            client,
            "visit-hidden-actions@example.com",
        )

        response = client.get(
            f"/clinic/day/{date.today().isoformat()}"
        )

        assert response.status_code == 200

        cancel_url = (
            f"/appointments/{appointment.uuid}"
            "/cancel/modal"
        ).encode()

        reschedule_url = (
            f"/appointments/{appointment.uuid}"
            "/reschedule/modal"
        ).encode()

        assert cancel_url not in response.data
        assert reschedule_url not in response.data

        db.drop_all()



def test_close_day_preview_and_htmx_success():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "close-day-htmx@example.com",
            "01099000021",
        )
        patient = create_patient(99021)

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        client = app.test_client()
        login(client, "close-day-htmx@example.com")

        preview = client.get(
            f"/clinic/day/{date.today().isoformat()}"
            "/close/preview"
        )

        assert preview.status_code == 200
        assert b"Close Clinic Day" in preview.data
        assert b"Will become no-show" in preview.data
        assert b"Visit completion is not changed automatically" in preview.data

        response = client.post(
            f"/clinic/day/{date.today().isoformat()}/close",
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 204
        trigger = json.loads(response.headers["HX-Trigger"])
        assert "clinic:action-success" in trigger

        db.session.refresh(appointment)
        assert appointment.status == Appointment.STATUS_NO_SHOW

        repeated = client.post(
            f"/clinic/day/{date.today().isoformat()}/close",
            headers={"HX-Request": "true"},
        )
        assert repeated.status_code == 204

        db.drop_all()


def test_emergency_modal_search_and_create():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "emergency-htmx@example.com",
            "01099000022",
        )
        patient = create_patient(99022)

        client = app.test_client()
        login(client, "emergency-htmx@example.com")

        modal = client.get(
            "/appointments/emergency/modal"
            "?q=HTMX"
        )

        assert modal.status_code == 200
        assert b"Add Emergency Patient" in modal.data
        assert str(patient.id).encode() in modal.data

        response = client.post(
            "/appointments/emergency",
            data={
                "patient_id": str(patient.id),
                "notes": "Urgent walk-in",
            },
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 204

        appointment = Appointment.query.filter_by(
            patient_id=patient.id,
            appointment_type=Appointment.TYPE_EMERGENCY,
        ).one()

        assert appointment.status == Appointment.STATUS_ARRIVED
        assert (
            appointment.source
            == Appointment.SOURCE_EMERGENCY_UNSCHEDULED
        )
        assert appointment.notes == "Urgent walk-in"

        db.drop_all()


def test_emergency_modal_requires_patient():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "emergency-invalid@example.com",
            "01099000023",
        )

        client = app.test_client()
        login(client, "emergency-invalid@example.com")

        response = client.post(
            "/appointments/emergency",
            data={"patient_id": "", "notes": ""},
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 200
        assert b"This field is required." in response.data

        db.drop_all()


def test_quick_edit_modal_and_success():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "quick-edit@example.com",
            "01099000024",
        )
        patient = create_patient(99024)

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        client = app.test_client()
        login(client, "quick-edit@example.com")

        modal = client.get(
            f"/appointments/{appointment.uuid}"
            "/quick-edit/modal"
        )

        assert modal.status_code == 200
        assert b"Quick Edit Appointment" in modal.data
        assert b"Patient, appointment date, and source cannot be changed here." in modal.data

        response = client.post(
            f"/appointments/{appointment.uuid}/quick-edit",
            data={
                "appointment_time": "15:30",
                "appointment_type": Appointment.TYPE_EMERGENCY,
                "fee_amount": "500.00",
                "paid_amount": "200.00",
                "payment_method": "cash",
                "notes": "Updated from Today Clinic",
            },
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 204

        db.session.refresh(appointment)
        assert appointment.appointment_time.strftime("%H:%M") == "15:30"
        assert appointment.appointment_type == Appointment.TYPE_EMERGENCY
        assert appointment.notes == "Updated from Today Clinic"
        assert appointment.fee_amount == Decimal("500.00")
        assert appointment.paid_amount == Decimal("200.00")

        charge = FinanceCharge.query.filter_by(
            source_type=FinanceCharge.SOURCE_APPOINTMENT,
            source_id=appointment.id,
        ).one()

        assert charge.net_amount == Decimal("500.00")
        assert charge.paid_amount == Decimal("200.00")

        db.drop_all()


def test_new_3b_actions_block_doctor_role():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Doctor",
            "doctor-rest-3b@example.com",
            "01099000025",
        )
        patient = create_patient(99025)

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        client = app.test_client()
        login(client, "doctor-rest-3b@example.com")

        responses = [
            client.get("/appointments/emergency/modal"),
            client.post(
                "/appointments/emergency",
                data={
                    "patient_id": str(patient.id),
                    "notes": "",
                },
            ),
            client.get(
                f"/appointments/{appointment.uuid}"
                "/quick-edit/modal"
            ),
            client.post(
                f"/appointments/{appointment.uuid}/quick-edit",
                data={
                    "appointment_type": Appointment.TYPE_FOLLOW_UP,
                },
            ),
            client.get(
                f"/clinic/day/{date.today().isoformat()}"
                "/close/preview"
            ),
            client.post(
                f"/clinic/day/{date.today().isoformat()}"
                "/close"
            ),
        ]

        assert all(
            response.status_code == 403
            for response in responses
        )

        db.drop_all()



def test_today_clinic_card_opens_workspace_without_extra_buttons():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Doctor",
            "card-workspace@example.com",
            "01099000026",
        )
        patient = create_patient(99026)

        AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
        )

        client = app.test_client()
        login(client, "card-workspace@example.com")

        response = client.get(
            f"/clinic/day/{date.today().isoformat()}"
        )

        assert response.status_code == 200
        assert b"data-workspace-url=" in response.data
        assert (
            f"/patients/{patient.uuid}".encode()
            in response.data
        )
        assert b"Open Workspace" not in response.data
        assert b"Manage Booking" not in response.data

        db.drop_all()


def test_appointment_forms_do_not_render_duration():
    app = make_app()

    with app.app_context():
        db.create_all()

        create_user(
            "Reception",
            "duration-hidden@example.com",
            "01099000027",
        )
        patient = create_patient(99027)

        appointment = AppointmentService.create_appointment(
            patient_id=patient.id,
            appointment_date=date.today(),
            appointment_type=Appointment.TYPE_FOLLOW_UP,
            duration_minutes=45,
        )

        client = app.test_client()
        login(client, "duration-hidden@example.com")

        responses = [
            client.get(
                f"/appointments/new"
                f"?patient_uuid={patient.uuid}"
            ),
            client.get(
                f"/appointments/{appointment.uuid}/edit"
            ),
            client.get(
                f"/appointments/{appointment.uuid}"
                "/quick-edit/modal"
            ),
        ]

        assert all(
            response.status_code == 200
            for response in responses
        )

        for response in responses:
            assert b"duration_minutes" not in response.data
            assert b"Duration minutes" not in response.data

        db.session.refresh(appointment)

        assert appointment.duration_minutes == 45

        db.drop_all()
