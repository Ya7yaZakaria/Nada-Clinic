from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class InvestigationResultForm(FlaskForm):
    result_date = DateField("Result date", validators=[DataRequired()])
    lab_name = StringField("Lab name", validators=[Optional(), Length(max=160)])

    result_value = StringField("Result value", validators=[Optional(), Length(max=160)])
    unit = StringField("Unit", validators=[Optional(), Length(max=80)])
    reference_range = StringField("Reference range", validators=[Optional(), Length(max=160)])

    result_text = TextAreaField("Result text / report summary", validators=[Optional(), Length(max=5000)])
    doctor_comment = TextAreaField("Doctor comment", validators=[Optional(), Length(max=5000)])

    abnormal_flag = SelectField("Abnormal flag", validators=[DataRequired()])
    has_attachment = BooleanField("Patient has external report / attachment placeholder")
    attachment_label = StringField("Attachment label", validators=[Optional(), Length(max=160)])
    external_report_reference = StringField("External report reference", validators=[Optional(), Length(max=255)])

    submit = SubmitField("Save result")


class HistoricalInvestigationResultForm(InvestigationResultForm):
    test_id = SelectField("Investigation test", coerce=int, validators=[DataRequired()])
