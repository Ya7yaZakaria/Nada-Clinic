from flask_wtf import FlaskForm
from wtforms import SubmitField


class SettingsUpdateForm(FlaskForm):
    """CSRF wrapper for legacy grouped settings update requests."""

    pass


class SettingEditForm(FlaskForm):
    """CSRF wrapper for editing a single setting value."""

    submit = SubmitField("Save setting")


class SettingsSeedDefaultsForm(FlaskForm):
    """CSRF wrapper for seeding/updating default settings."""

    submit = SubmitField("Seed defaults")
