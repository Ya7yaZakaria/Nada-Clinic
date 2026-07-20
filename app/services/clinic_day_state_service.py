from datetime import UTC, datetime

from werkzeug.exceptions import Conflict

from app.extensions import db
from app.models.clinic_day_state import ClinicDayState


class ClinicDayStateService:
    """Persistent open/closed state for a clinic date."""

    @staticmethod
    def get_state(clinic_date):
        return ClinicDayState.query.filter_by(
            clinic_date=clinic_date
        ).first()

    @classmethod
    def is_closed(cls, clinic_date):
        state = cls.get_state(clinic_date)
        return bool(state and state.is_closed)

    @classmethod
    def require_open(cls, clinic_date):
        if cls.is_closed(clinic_date):
            raise Conflict("Clinic day is closed.")

        return True

    @classmethod
    def close_day(cls, clinic_date, *, commit=True):
        state = cls.get_state(clinic_date)

        if state is None:
            state = ClinicDayState(
                clinic_date=clinic_date,
            )
            db.session.add(state)

        if state.is_closed:
            raise Conflict(
                "Clinic day is already closed."
            )

        state.is_closed = True
        state.closed_at = datetime.now(UTC)

        if commit:
            db.session.commit()
        else:
            db.session.flush()

        return state

    @classmethod
    def reopen_day(cls, clinic_date, *, commit=True):
        state = cls.get_state(clinic_date)

        if state is None or not state.is_closed:
            raise Conflict(
                "Clinic day is already open."
            )

        state.is_closed = False
        state.reopened_at = datetime.now(UTC)

        if commit:
            db.session.commit()
        else:
            db.session.flush()

        return state