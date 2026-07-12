from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class DrugForm(FlaskForm):
    generic_name = StringField(
        "Generic name",
        validators=[
            DataRequired(),
            Length(max=160),
        ],
    )
    trade_name = StringField(
        "Trade name",
        validators=[
            DataRequired(),
            Length(max=160),
        ],
    )
    strength = StringField(
        "Strength",
        validators=[
            DataRequired(),
            Length(max=80),
        ],
    )

    category_id = SelectField("Category", coerce=int, validators=[Optional()])
    form_id = SelectField("Form", coerce=int, validators=[DataRequired()])
    route_id = SelectField("Route", coerce=int, validators=[Optional()])

    pregnancy_status_id = SelectField("Pregnancy status", coerce=int, validators=[Optional()])
    pregnancy_note = TextAreaField("Pregnancy note", validators=[Optional(), Length(max=2000)])

    lactation_status_id = SelectField("Lactation status", coerce=int, validators=[Optional()])
    lactation_note = TextAreaField("Lactation note", validators=[Optional(), Length(max=2000)])

    doctor_notes = TextAreaField("Doctor notes", validators=[Optional(), Length(max=2000)])

    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save")
