from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.models import Journey
from app.services.journey_service import JourneyService


class JourneyForm(FlaskForm):
    journey_type = SelectField(
        "Journey type",
        choices=[
            ("pregnancy", "Pregnancy"),
            ("gynecology", "Gynecology"),
            ("infertility", "Infertility"),
        ],
        validators=[DataRequired()],
    )
    title = StringField(
        "Title",
        validators=[DataRequired(), Length(max=180)],
    )
    description = TextAreaField(
        "Description",
        validators=[Optional()],
    )
    start_date = StringField(
        "Start date",
        validators=[DataRequired()],
        description="Accepts YYYY, YYYY-MM, or YYYY-MM-DD.",
    )
    submit = SubmitField("Save journey")

    def validate_start_date(self, field):
        JourneyService.parse_flexible_date(field.data)


class CloseJourneyForm(FlaskForm):
    end_date = StringField(
        "End date",
        validators=[DataRequired()],
        description="Accepts YYYY, YYYY-MM, or YYYY-MM-DD.",
    )
    outcome = SelectField(
        "Outcome",
        choices=[],
        validators=[DataRequired()],
    )
    outcome_note = TextAreaField(
        "Outcome note",
        validators=[Optional()],
    )
    confirm_close = BooleanField("I understand this will close the journey.")
    submit = SubmitField("Close journey")

    def __init__(self, *args, journey_type=None, **kwargs):
        super().__init__(*args, **kwargs)

        if journey_type:
            self.outcome.choices = [
                (outcome, JourneyService.get_outcome_label(outcome))
                for outcome in JourneyService.get_outcome_choices(journey_type)
            ]

    def validate_end_date(self, field):
        JourneyService.parse_flexible_date(field.data)

    def validate_confirm_close(self, field):
        if not field.data:
            raise ValidationError("You must confirm journey closure.")


class ReopenJourneyForm(FlaskForm):
    confirm_reopen = BooleanField("I understand this will reopen the journey.")
    submit = SubmitField("Reopen journey")

    def validate_confirm_reopen(self, field):
        if not field.data:
            raise ValidationError("You must confirm journey reopening.")
