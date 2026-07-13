from flask_wtf import FlaskForm
from wtforms import BooleanField, FloatField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

from app.models.print_template import PrintTemplate


class PrintTemplateForm(FlaskForm):
    document_type = SelectField(
        "Document type",
        choices=[
            (PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION, "Prescription"),
            (PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST, "Investigation Request"),
        ],
        validators=[DataRequired()],
    )
    name = StringField(
        "Template name",
        validators=[DataRequired(), Length(max=160)],
    )
    paper_width_mm = FloatField(
        "Paper width (mm)",
        validators=[DataRequired(), NumberRange(min=1, max=1000)],
    )
    paper_height_mm = FloatField(
        "Paper height (mm)",
        validators=[DataRequired(), NumberRange(min=1, max=1000)],
    )
    is_default = BooleanField("Default for this document type")
    is_active = BooleanField("Active")
    submit = SubmitField("Save template")
