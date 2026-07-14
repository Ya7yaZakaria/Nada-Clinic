from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from app.models import ClinicUltrasoundExam


class ClinicUltrasoundForm(FlaskForm):
    exam_type = SelectField(
        "Ultrasound type",
        choices=[
            (ClinicUltrasoundExam.EXAM_TYPE_OBS, "OBS"),
            (ClinicUltrasoundExam.EXAM_TYPE_GYNE, "Gyne"),
            (ClinicUltrasoundExam.EXAM_TYPE_OI_TI, "OI/TI"),
            (ClinicUltrasoundExam.EXAM_TYPE_OTHER, "Other"),
        ],
        validators=[DataRequired()],
        default=ClinicUltrasoundExam.EXAM_TYPE_OBS,
    )

    exam_route = SelectField(
        "Route",
        choices=[
            (ClinicUltrasoundExam.ROUTE_UNKNOWN, "Unknown"),
            (ClinicUltrasoundExam.ROUTE_TRANSABDOMINAL, "Transabdominal"),
            (ClinicUltrasoundExam.ROUTE_TRANSVAGINAL, "Transvaginal"),
            (ClinicUltrasoundExam.ROUTE_BOTH, "Both"),
        ],
        validators=[DataRequired()],
        default=ClinicUltrasoundExam.ROUTE_UNKNOWN,
    )

    # OBS fields
    pregnancy_count = StringField("Pregnancy count", validators=[Optional()])
    viability = StringField("Viability", validators=[Optional()])
    presentation = StringField("Presentation", validators=[Optional()])
    fetal_heart = StringField("Fetal heart", validators=[Optional()])
    fhr = StringField("FHR", validators=[Optional()])
    bpd_ga = StringField("BPD GA", validators=[Optional()])
    hc_ga = StringField("HC GA", validators=[Optional()])
    ac_ga = StringField("AC GA", validators=[Optional()])
    fl_ga = StringField("FL GA", validators=[Optional()])
    efw = StringField("EFW", validators=[Optional()])
    ga_by_ultrasound = StringField("GA by ultrasound", validators=[Optional()])
    placenta = StringField("Placenta", validators=[Optional()])
    liquor = StringField("Liquor", validators=[Optional()])
    afi = StringField("AFI", validators=[Optional()])

    # Gyne fields
    uterus_note = TextAreaField("Uterus note", validators=[Optional()])
    endometrium_thickness = StringField("Endometrium thickness", validators=[Optional()])
    endometrium_appearance = StringField("Endometrium appearance", validators=[Optional()])
    endometrium_note = TextAreaField("Endometrium note", validators=[Optional()])
    right_ovary_status = StringField("Right ovary status", validators=[Optional()])
    right_ovary_note = TextAreaField("Right ovary note", validators=[Optional()])
    left_ovary_status = StringField("Left ovary status", validators=[Optional()])
    left_ovary_note = TextAreaField("Left ovary note", validators=[Optional()])
    adnexa_note = TextAreaField("Adnexa note", validators=[Optional()])
    free_fluid = StringField("Free fluid", validators=[Optional()])

    # OI/TI fields
    cycle_day = StringField("Cycle day", validators=[Optional()])
    stimulation_day = StringField("Stimulation day", validators=[Optional()])
    endometrium_thickness_oi = StringField("Endometrium thickness", validators=[Optional()])
    endometrium_pattern = StringField("Endometrium pattern", validators=[Optional()])
    right_follicle_sizes = StringField("Right follicle sizes", validators=[Optional()])
    left_follicle_sizes = StringField("Left follicle sizes", validators=[Optional()])
    right_ovary_extra = TextAreaField("Right ovary extra findings", validators=[Optional()])
    left_ovary_extra = TextAreaField("Left ovary extra findings", validators=[Optional()])
    uterus_myoma_note = TextAreaField("Uterus / myoma note", validators=[Optional()])
    cyst_endometrioma_note = TextAreaField("Cyst / endometrioma note", validators=[Optional()])
    adnexa_free_fluid_note = TextAreaField("Adnexa / free fluid note", validators=[Optional()])

    # Common text fields
    findings_text = TextAreaField("Findings text", validators=[Optional()])
    extra_note = TextAreaField("Extra note", validators=[Optional()])
    impression = TextAreaField("Impression", validators=[Optional()])
    sketch_note = TextAreaField("Sketch note", validators=[Optional()])

    submit = SubmitField("Save ultrasound")

    OBS_KEYS = [
        "pregnancy_count",
        "viability",
        "presentation",
        "fetal_heart",
        "fhr",
        "bpd_ga",
        "hc_ga",
        "ac_ga",
        "fl_ga",
        "efw",
        "ga_by_ultrasound",
        "placenta",
        "liquor",
        "afi",
    ]

    GYNE_KEYS = [
        "uterus_note",
        "endometrium_thickness",
        "endometrium_appearance",
        "endometrium_note",
        "right_ovary_status",
        "right_ovary_note",
        "left_ovary_status",
        "left_ovary_note",
        "adnexa_note",
        "free_fluid",
    ]

    OI_TI_KEYS = [
        "cycle_day",
        "stimulation_day",
        "endometrium_thickness_oi",
        "endometrium_pattern",
        "right_follicle_sizes",
        "left_follicle_sizes",
        "right_ovary_extra",
        "left_ovary_extra",
        "uterus_myoma_note",
        "cyst_endometrioma_note",
        "adnexa_free_fluid_note",
    ]

    @staticmethod
    def _clean(value):
        return (value or "").strip()

    def _extract_keys(self, keys):
        data = {}

        for key in keys:
            value = self._clean(getattr(self, key).data)
            if value:
                data[key] = value

        return data

    def build_findings_json(self):
        exam_type = self.exam_type.data

        if exam_type == ClinicUltrasoundExam.EXAM_TYPE_OBS:
            return self._extract_keys(self.OBS_KEYS)

        if exam_type == ClinicUltrasoundExam.EXAM_TYPE_GYNE:
            return self._extract_keys(self.GYNE_KEYS)

        if exam_type == ClinicUltrasoundExam.EXAM_TYPE_OI_TI:
            return self._extract_keys(self.OI_TI_KEYS)

        return {}

    def apply_exam(self, exam):
        self.exam_type.data = exam.exam_type
        self.exam_route.data = exam.exam_route

        findings = exam.findings_json or {}

        for key in self.OBS_KEYS + self.GYNE_KEYS + self.OI_TI_KEYS:
            if hasattr(self, key):
                getattr(self, key).data = findings.get(key, "")

        self.findings_text.data = exam.findings_text or ""
        self.extra_note.data = exam.extra_note or ""
        self.impression.data = exam.impression or ""
        self.sketch_note.data = exam.sketch_note or ""
