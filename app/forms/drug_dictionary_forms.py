from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class DrugDictionaryForm(FlaskForm):
    code = StringField(
        "Code",
        validators=[
            DataRequired(),
            Length(max=80),
        ],
    )
    name_en = StringField(
        "English name",
        validators=[
            DataRequired(),
            Length(max=120),
        ],
    )
    name_ar = StringField(
        "Arabic name",
        validators=[
            Optional(),
            Length(max=120),
        ],
    )
    sort_order = IntegerField(
        "Sort order",
        validators=[
            Optional(),
            NumberRange(min=0),
        ],
        default=0,
    )
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save")


class DrugSafetyStatusForm(DrugDictionaryForm):
    severity_order = IntegerField(
        "Severity order",
        validators=[
            Optional(),
            NumberRange(min=0),
        ],
        default=0,
    )
