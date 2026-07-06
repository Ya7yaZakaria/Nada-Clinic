from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    login_identifier = StringField(
        "Email or phone",
        validators=[DataRequired(), Length(max=255)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=128)],
    )
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")
