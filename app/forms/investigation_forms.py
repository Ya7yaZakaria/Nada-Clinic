from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import Length, Optional


class InvestigationOrderForm(FlaskForm):
    priority = SelectField(
        "Priority",
        choices=[
            ("routine", "Routine"),
            ("important", "Important"),
            ("urgent", "Urgent"),
        ],
        validators=[Optional()],
    )
    order_notes = TextAreaField(
        "Order notes",
        validators=[Optional(), Length(max=2000)],
    )
    submit = SubmitField("Create investigation order")


class InvestigationOrderItemForm(FlaskForm):
    test_id = SelectField("Investigation test", coerce=int, validators=[Optional()])
    item_notes = StringField("Item notes", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Add test")
