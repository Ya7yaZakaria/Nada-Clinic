from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, HiddenField, IntegerField, SelectField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

from app.models.appointment import Appointment
from app.services.finance_service import FinanceService


class AppointmentForm(FlaskForm):
    patient_id = HiddenField("Patient ID", validators=[DataRequired()])

    appointment_date = DateField(
        "Appointment date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
        default=date.today,
    )

    appointment_time = TimeField(
        "Appointment time",
        validators=[Optional()],
        format="%H:%M",
    )

    duration_minutes = IntegerField(
        "Duration minutes",
        validators=[Optional(), NumberRange(min=5, max=240)],
    )

    appointment_type = SelectField(
        "Appointment type",
        choices=[
            (Appointment.TYPE_NEW_CONSULTATION, "كشف"),
            (Appointment.TYPE_FOLLOW_UP, "إعادة كشف"),
            (Appointment.TYPE_EMERGENCY, "طوارئ"),
        ],
        validators=[DataRequired()],
    )

    source = SelectField(
        "Source",
        choices=[
            (Appointment.SOURCE_CLINIC, "Clinic"),
            (Appointment.SOURCE_PHONE, "Phone"),
            (Appointment.SOURCE_WHATSAPP, "WhatsApp"),
            (Appointment.SOURCE_EMERGENCY_UNSCHEDULED, "Emergency unscheduled"),
        ],
        default=Appointment.SOURCE_CLINIC,
        validators=[DataRequired()],
    )

    fee_amount = DecimalField("Fee", places=2, validators=[Optional(), NumberRange(min=0)])
    paid_amount = DecimalField("Paid now", places=2, validators=[Optional(), NumberRange(min=0)])
    payment_method = SelectField("Payment method", choices=[("", "Not paid")] + FinanceService.payment_method_choices(), validators=[Optional()])

    notes = TextAreaField(
        "Notes",
        validators=[Optional(), Length(max=2000)],
    )

    submit = SubmitField("Save appointment")

    def validate_appointment_type(self, field):
        if field.data not in Appointment.VALID_TYPES:
            raise ValidationError("Invalid appointment type.")

    def validate_source(self, field):
        if field.data not in Appointment.VALID_SOURCES:
            raise ValidationError("Invalid appointment source.")


class AppointmentPatientSearchForm(FlaskForm):
    q = StringField("Patient search", validators=[Optional(), Length(max=120)])


class AppointmentCancelForm(FlaskForm):
    reason = TextAreaField(
        "Cancel reason",
        validators=[
            DataRequired(),
            Length(max=1000),
        ],
    )
    submit = SubmitField("Cancel appointment")


class AppointmentRescheduleForm(FlaskForm):
    appointment_date = DateField(
        "New appointment date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
    )

    appointment_time = TimeField(
        "New appointment time",
        validators=[Optional()],
        format="%H:%M",
    )

    submit = SubmitField("Reschedule appointment")


class AppointmentEmergencyForm(FlaskForm):
    patient_id = HiddenField(
        "Patient ID",
        validators=[DataRequired()],
    )
    notes = TextAreaField(
        "Notes",
        validators=[Optional(), Length(max=2000)],
    )
    submit = SubmitField("Add Emergency Patient")


class AppointmentQuickEditForm(FlaskForm):
    appointment_time = TimeField(
        "Appointment time",
        validators=[Optional()],
        format="%H:%M",
    )
    duration_minutes = IntegerField(
        "Duration minutes",
        validators=[Optional(), NumberRange(min=5, max=240)],
    )
    appointment_type = SelectField(
        "Appointment type",
        choices=[
            (Appointment.TYPE_NEW_CONSULTATION, "كشف"),
            (Appointment.TYPE_FOLLOW_UP, "إعادة كشف"),
            (Appointment.TYPE_EMERGENCY, "طوارئ"),
        ],
        validators=[DataRequired()],
    )
    fee_amount = DecimalField(
        "Fee",
        places=2,
        validators=[Optional(), NumberRange(min=0)],
    )
    paid_amount = DecimalField(
        "Paid now",
        places=2,
        validators=[Optional(), NumberRange(min=0)],
    )
    payment_method = SelectField(
        "Payment method",
        choices=[("", "Not paid")]
        + FinanceService.payment_method_choices(),
        validators=[Optional()],
    )
    notes = TextAreaField(
        "Notes",
        validators=[Optional(), Length(max=2000)],
    )
    submit = SubmitField("Save Quick Edit")

    def validate_appointment_type(self, field):
        if field.data not in Appointment.VALID_TYPES:
            raise ValidationError("Invalid appointment type.")


class AppointmentArriveForm(FlaskForm):
    submit = SubmitField("Mark arrived")
