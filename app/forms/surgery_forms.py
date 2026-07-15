from datetime import datetime, timezone

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, HiddenField, SelectField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Length, Optional

from app.models.surgery import SurgeryCase
from app.services.surgery_service import SurgeryService


class SurgeryForm(FlaskForm):
    patient_id = SelectField("Patient", coerce=int, validators=[Optional()])
    procedure_name = StringField("Procedure", validators=[DataRequired(), Length(max=160)])
    procedure_category = SelectField("Category", validators=[DataRequired()])
    scheduled_date = DateField("Date", validators=[DataRequired()])
    scheduled_time = TimeField("Time", validators=[DataRequired()])
    location = StringField("Location", validators=[Optional(), Length(max=160)])
    priority = SelectField("Priority", validators=[DataRequired()])
    pre_op_note = TextAreaField("Pre-op note", validators=[Optional()])
    surgery_note = TextAreaField("Surgery note", validators=[Optional()])
    fee_amount = DecimalField("Fee", places=2, validators=[Optional()])
    paid_amount = DecimalField("Paid", places=2, validators=[Optional()])
    payment_status = SelectField("Payment status", validators=[Optional()])
    payment_method = SelectField("Payment method", validators=[Optional()])
    submit = SubmitField("Save Surgery")

    def set_choices(self, patient_choices=None):
        self.patient_id.choices = patient_choices or [(0, "Select patient...")]
        self.procedure_category.choices = SurgeryService.category_choices()
        self.priority.choices = SurgeryService.priority_choices()
        self.payment_status.choices = [("", "Auto / not recorded")] + SurgeryService.payment_choices()
        self.payment_method.choices = [("", "Not paid")] + SurgeryService.payment_method_choices()

    def scheduled_at(self):
        if not self.scheduled_date.data or not self.scheduled_time.data:
            return None
        return datetime.combine(self.scheduled_date.data, self.scheduled_time.data).replace(tzinfo=timezone.utc)

    def apply_surgery(self, surgery):
        self.procedure_name.data = surgery.procedure_name
        self.procedure_category.data = surgery.procedure_category
        self.scheduled_date.data = surgery.scheduled_at.date()
        self.scheduled_time.data = surgery.scheduled_at.time().replace(second=0, microsecond=0)
        self.location.data = surgery.location
        self.priority.data = surgery.priority
        self.pre_op_note.data = surgery.pre_op_note
        self.surgery_note.data = surgery.surgery_note
        self.fee_amount.data = surgery.fee_amount
        self.paid_amount.data = surgery.paid_amount
        self.payment_status.data = surgery.payment_status or ""
        self.payment_method.data = surgery.payment_method or ""


class SurgeryCompleteForm(FlaskForm):
    completed_date = DateField("Completed date", validators=[DataRequired()])
    completed_time = TimeField("Completed time", validators=[DataRequired()])
    operative_findings = TextAreaField("Operative findings", validators=[Optional()])
    operative_details = TextAreaField("Operative details", validators=[Optional()])
    complications = TextAreaField("Complications", validators=[Optional()])
    post_op_plan = TextAreaField("Post-op plan", validators=[Optional()])
    fee_amount = DecimalField("Fee", places=2, validators=[Optional()])
    paid_amount = DecimalField("Paid", places=2, validators=[Optional()])
    payment_status = SelectField("Payment status", validators=[Optional()])
    payment_method = SelectField("Payment method", validators=[Optional()])
    submit = SubmitField("Complete Surgery")

    def set_choices(self):
        self.payment_status.choices = [("", "Auto / keep current")] + SurgeryService.payment_choices()
        self.payment_method.choices = [("", "Keep current / not paid")] + SurgeryService.payment_method_choices()

    def completed_at(self):
        if not self.completed_date.data or not self.completed_time.data:
            return None
        return datetime.combine(self.completed_date.data, self.completed_time.data).replace(tzinfo=timezone.utc)


class SurgeryCancelForm(FlaskForm):
    cancel_reason = TextAreaField("Cancel reason", validators=[DataRequired()])
    submit = SubmitField("Cancel Surgery")


class SurgeryPostponeForm(FlaskForm):
    new_scheduled_date = DateField("New date", validators=[DataRequired()])
    new_scheduled_time = TimeField("New time", validators=[DataRequired()])
    postponed_reason = TextAreaField("Postponed reason", validators=[DataRequired()])
    submit = SubmitField("Postpone Surgery")

    def new_scheduled_at(self):
        if not self.new_scheduled_date.data or not self.new_scheduled_time.data:
            return None
        return datetime.combine(self.new_scheduled_date.data, self.new_scheduled_time.data).replace(tzinfo=timezone.utc)
