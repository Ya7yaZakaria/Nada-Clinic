from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError


class PatientForm(FlaskForm):
    name_ar = StringField(
        "Arabic name",
        validators=[DataRequired(), Length(max=160)],
    )
    name_en = StringField(
        "English name",
        validators=[DataRequired(), Length(max=160)],
    )

    phone_primary = StringField(
        "Primary phone",
        validators=[DataRequired(), Length(max=40)],
    )
    phone_secondary = StringField(
        "Secondary phone",
        validators=[Optional(), Length(max=40)],
    )
    email = StringField(
        "Email",
        validators=[Optional(), Email(), Length(max=255)],
    )

    date_of_birth = DateField(
        "Date of birth",
        validators=[Optional()],
        format="%Y-%m-%d",
    )
    age_years_at_registration = IntegerField(
        "Manual age",
        validators=[Optional(), NumberRange(min=0, max=120)],
    )

    marital_status = SelectField(
        "Marital status",
        choices=[
            ("unknown", "Unknown"),
            ("single", "Single"),
            ("married", "Married"),
            ("divorced", "Divorced"),
            ("widowed", "Widowed"),
        ],
        default="unknown",
        validators=[DataRequired()],
    )
    is_virgin = BooleanField("Virgin")

    occupation = StringField(
        "Occupation",
        validators=[Optional(), Length(max=120)],
    )

    governorate = StringField(
        "Governorate",
        validators=[Optional(), Length(max=120)],
    )
    city = StringField(
        "City",
        validators=[Optional(), Length(max=120)],
    )
    street = StringField(
        "Street",
        validators=[Optional(), Length(max=255)],
    )

    submit = SubmitField("Save patient")

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)

        if not self.date_of_birth.data and self.age_years_at_registration.data is None:
            self.age_years_at_registration.errors.append(
                "Date of birth or manual age is required."
            )
            return False

        return is_valid


class MRNChangeForm(FlaskForm):
    medical_file_number = IntegerField(
        "Medical file number",
        validators=[DataRequired(), NumberRange(min=1)],
    )
    confirm_mrn_change = BooleanField("I understand this changes the patient file number.")
    submit = SubmitField("Change MRN")

    def validate_confirm_mrn_change(self, field):
        if not field.data:
            raise ValidationError("You must confirm the MRN change warning.")
