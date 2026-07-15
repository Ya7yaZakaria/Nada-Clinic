from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import DateField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class PartnerForm(FlaskForm):
    name = StringField("Partner name", validators=[DataRequired(), Length(max=160)])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    age_years = IntegerField("Age", validators=[Optional(), NumberRange(min=0, max=120)])
    occupation = StringField("Occupation", validators=[Optional(), Length(max=160)])

    previous_children = TextAreaField("Previous children", validators=[Optional(), Length(max=2000)])
    fertility_notes = TextAreaField("Fertility notes", validators=[Optional(), Length(max=3000)])
    medical_notes = TextAreaField("Medical notes", validators=[Optional(), Length(max=3000)])

    follow_up_note = TextAreaField("Follow-up note", validators=[Optional(), Length(max=2000)])
    follow_up_date = DateField("Follow-up date", validators=[Optional()])

    submit = SubmitField("Save partner")


class PartnerSemenAnalysisForm(FlaskForm):
    analysis_date = DateField("Analysis date", validators=[DataRequired()])
    notes = TextAreaField("Notes / summary", validators=[Optional(), Length(max=4000)])
    file = FileField(
        "Upload SA image/PDF",
        validators=[
            Optional(),
            FileAllowed(["pdf", "png", "jpg", "jpeg", "webp", "gif", "txt"], "Unsupported file type."),
        ],
    )
    submit = SubmitField("Save semen analysis")


class PartnerPrescriptionForm(FlaskForm):
    notes = TextAreaField("Prescription notes", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Create prescription")
