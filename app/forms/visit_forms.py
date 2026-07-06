from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from app.services.journey_service import JourneyService


class VisitForm(FlaskForm):
    visit_type = SelectField(
        "Visit type",
        choices=[
            ("obs", "OBS"),
            ("gyn", "Gyn"),
            ("infertility", "Infertility"),
            ("oiti", "OITI"),
            ("iui", "IUI"),
            ("procedure", "Procedure"),
            ("general", "General"),
        ],
        validators=[DataRequired()],
        default="general",
    )

    journey_id = SelectField(
        "Journey",
        choices=[],
        validators=[Optional()],
    )

    chief_complaint = TextAreaField("Chief complaint", validators=[Optional()])
    history = TextAreaField("History", validators=[Optional()])
    examination = TextAreaField("Examination", validators=[Optional()])
    assessment = TextAreaField("Assessment", validators=[Optional()])
    plan = TextAreaField("Plan", validators=[Optional()])
    follow_up_date = StringField("Follow-up date", validators=[Optional()])

    submit = SubmitField("Save visit")

    def set_journey_choices(self, journeys):
        self.journey_id.choices = [("", "No Journey / Standalone Visit")]

        for journey in journeys:
            label = (
                f"{JourneyService.get_type_label(journey.journey_type)} — "
                f"{journey.title} ({JourneyService.get_status_label(journey.status)})"
            )
            self.journey_id.choices.append((str(journey.id), label))


class VisitJourneyLinkForm(FlaskForm):
    journey_id = SelectField(
        "Journey",
        choices=[],
        validators=[Optional()],
    )
    submit = SubmitField("Update journey link")

    def set_journey_choices(self, journeys):
        self.journey_id.choices = [("", "No Journey / Standalone Visit")]

        for journey in journeys:
            label = (
                f"{JourneyService.get_type_label(journey.journey_type)} — "
                f"{journey.title} ({JourneyService.get_status_label(journey.status)})"
            )
            self.journey_id.choices.append((str(journey.id), label))
