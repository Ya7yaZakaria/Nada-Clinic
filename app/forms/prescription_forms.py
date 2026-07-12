from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class PrescriptionItemForm(FlaskForm):
    drug_id = SelectField("Drug", coerce=int, validators=[DataRequired()])
    route_id = SelectField("Route override", coerce=int, validators=[Optional()])

    dose = StringField("Dose", validators=[DataRequired(), Length(max=120)])
    frequency = StringField("Frequency", validators=[DataRequired(), Length(max=120)])
    duration = StringField("Duration", validators=[DataRequired(), Length(max=120)])
    instructions_ar = TextAreaField(
        "Arabic instructions",
        validators=[DataRequired(), Length(max=2000)],
    )

    submit = SubmitField("Save medication")
