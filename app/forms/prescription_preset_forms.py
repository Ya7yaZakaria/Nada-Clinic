from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class PrescriptionPresetForm(FlaskForm):
    name = StringField(
        "Preset name",
        validators=[
            DataRequired(),
            Length(max=160),
        ],
    )
    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=2000),
        ],
    )
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save preset")


class PrescriptionPresetItemForm(FlaskForm):
    drug_id = SelectField("Drug", coerce=int, validators=[DataRequired()])
    route_id = SelectField("Route override", coerce=int, validators=[Optional()])

    dose = StringField("Dose", validators=[DataRequired(), Length(max=120)])
    frequency = StringField("Frequency", validators=[DataRequired(), Length(max=120)])
    duration = StringField("Duration", validators=[DataRequired(), Length(max=120)])
    instructions_ar = TextAreaField(
        "Arabic instructions",
        validators=[DataRequired(), Length(max=2000)],
    )

    submit = SubmitField("Save preset item")
