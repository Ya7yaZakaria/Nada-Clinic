from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class InvestigationReviewForm(FlaskForm):
    abnormal_flag = SelectField("Confirm abnormal flag", validators=[DataRequired()])
    review_note = TextAreaField(
        "Review note",
        validators=[
            Optional(),
            Length(max=5000),
        ],
    )
    submit = SubmitField("Review result")
