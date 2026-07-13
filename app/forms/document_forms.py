from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app.models import PatientDocument


class DocumentUploadForm(FlaskForm):
    document_type = SelectField(
        "Document type",
        choices=[
            (PatientDocument.TYPE_INVESTIGATION_REPORT, "Investigation report"),
            (PatientDocument.TYPE_ULTRASOUND_IMAGE, "Ultrasound image"),
            (PatientDocument.TYPE_ULTRASOUND_REPORT, "Ultrasound report"),
            (PatientDocument.TYPE_OPERATION_REPORT, "Operation report"),
            (PatientDocument.TYPE_CONSENT, "Consent"),
            (PatientDocument.TYPE_ID_DOCUMENT, "ID document"),
            (PatientDocument.TYPE_INSURANCE, "Insurance"),
            (PatientDocument.TYPE_EXTERNAL_PRESCRIPTION, "External prescription"),
            (PatientDocument.TYPE_PHOTO, "Photo"),
            (PatientDocument.TYPE_OTHER, "Other"),
        ],
        validators=[DataRequired()],
    )

    title = StringField("Title", validators=[Optional(), Length(max=160)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])

    file = FileField(
        "File",
        validators=[
            FileRequired(),
            FileAllowed(
                ["pdf", "png", "jpg", "jpeg", "webp", "gif", "txt"],
                "Unsupported file type.",
            ),
        ],
    )

    submit = SubmitField("Upload document")
