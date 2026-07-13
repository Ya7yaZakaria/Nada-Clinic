from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class InvestigationPresetForm(FlaskForm):
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


class InvestigationPresetItemForm(FlaskForm):
    test_id = SelectField("Investigation test", coerce=int, validators=[DataRequired()])
    notes = StringField("Notes", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Save preset item")


class InvestigationPresetApplyForm(FlaskForm):
    preset_id = SelectField("Investigation preset", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Apply preset")
