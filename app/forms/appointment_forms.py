from datetime import date

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DecimalField, HiddenField, IntegerField, SelectField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError

from app.models.appointment import Appointment
from app.services.finance_service import FinanceService


def _validate_embedded_payment(form):
    paid_amount = form.paid_amount.data
    if paid_amount in (None, 0):
        return True

    is_valid = True
    if form.fee_amount.data is None:
        form.fee_amount.errors.append("Fee is required when recording a payment.")
        is_valid = False
    if not form.payment_method.data:
        form.payment_method.errors.append(
            "Payment method is required when Paid now is greater than zero."
        )
        is_valid = False
    return is_valid


class AppointmentPatientSelectionForm(FlaskForm):
    patient_mode = HiddenField("Patient mode", default="existing")
    patient_id = HiddenField("Patient ID", validators=[Optional()])

    new_patient_name_ar = StringField(
        "Arabic name",
        validators=[Optional(), Length(max=160)],
    )
    new_patient_name_en = StringField(
        "English name",
        validators=[Optional(), Length(max=160)],
    )
    new_patient_phone_primary = StringField(
        "Primary phone",
        validators=[Optional(), Length(max=40)],
    )
    new_patient_phone_secondary = StringField(
        "Secondary phone",
        validators=[Optional(), Length(max=40)],
    )
    new_patient_email = StringField(
        "Email",
        validators=[Optional(), Email(), Length(max=255)],
    )
    new_patient_date_of_birth = DateField(
        "Date of birth",
        validators=[Optional()],
        format="%Y-%m-%d",
    )
    new_patient_age_years_at_registration = IntegerField(
        "Manual age",
        validators=[Optional(), NumberRange(min=0, max=120)],
    )
    new_patient_marital_status = SelectField(
        "Marital status",
        choices=[
            ("unknown", "Unknown"),
            ("single", "Single"),
            ("married", "Married"),
            ("divorced", "Divorced"),
            ("widowed", "Widowed"),
        ],
        default="unknown",
        validators=[Optional()],
    )
    new_patient_is_virgin = BooleanField("Virgin")
    new_patient_occupation = StringField(
        "Occupation",
        validators=[Optional(), Length(max=120)],
    )
    new_patient_governorate = StringField(
        "Governorate",
        validators=[Optional(), Length(max=120)],
    )
    new_patient_city = StringField(
        "City",
        validators=[Optional(), Length(max=120)],
    )
    new_patient_street = StringField(
        "Street",
        validators=[Optional(), Length(max=255)],
    )

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)

        if self.patient_mode.data not in {"existing", "new"}:
            self.patient_mode.errors.append("Choose an existing or new patient.")
            return False

        if self.patient_mode.data == "existing":
            if not self.patient_id.data:
                self.patient_id.errors.append("This field is required.")
                return False
            return is_valid

        required_fields = (
            (self.new_patient_name_ar, "Arabic name is required."),
            (self.new_patient_name_en, "English name is required."),
            (self.new_patient_phone_primary, "Primary phone is required."),
        )
        for field, message in required_fields:
            if not (field.data or "").strip():
                field.errors.append(message)
                is_valid = False

        if (
            not self.new_patient_date_of_birth.data
            and self.new_patient_age_years_at_registration.data is None
        ):
            self.new_patient_age_years_at_registration.errors.append(
                "Date of birth or manual age is required."
            )
            is_valid = False

        return is_valid


class AppointmentForm(AppointmentPatientSelectionForm):

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

    appointment_type = SelectField(
        "Appointment type",
        choices=[
            (Appointment.TYPE_NEW_CONSULTATION, "New Consultation"),
            (Appointment.TYPE_FOLLOW_UP, "Follow-up"),
            (Appointment.TYPE_EMERGENCY, "Emergency"),
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

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)
        return _validate_embedded_payment(self) and is_valid

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


class AppointmentEmergencyForm(AppointmentPatientSelectionForm):
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
        choices=[("", "Not paid")] + FinanceService.payment_method_choices(),
        validators=[Optional()],
    )
    notes = TextAreaField(
        "Notes",
        validators=[Optional(), Length(max=2000)],
    )
    submit = SubmitField("Add Emergency Patient")

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)
        return _validate_embedded_payment(self) and is_valid


class AppointmentQuickEditForm(FlaskForm):
    appointment_time = TimeField(
        "Appointment time",
        validators=[Optional()],
        format="%H:%M",
    )
    appointment_type = SelectField(
        "Appointment type",
        choices=[
            (Appointment.TYPE_NEW_CONSULTATION, "New Consultation"),
            (Appointment.TYPE_FOLLOW_UP, "Follow-up"),
            (Appointment.TYPE_EMERGENCY, "Emergency"),
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

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)
        return _validate_embedded_payment(self) and is_valid

    def validate_appointment_type(self, field):
        if field.data not in Appointment.VALID_TYPES:
            raise ValidationError("Invalid appointment type.")


class AppointmentArriveForm(FlaskForm):
    submit = SubmitField("Mark arrived")
