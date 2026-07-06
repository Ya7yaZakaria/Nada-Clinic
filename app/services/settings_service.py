from app.extensions import db
from app.models import Setting


class SettingsService:
    """Settings service for grouped clinic/system settings."""

    DEFAULT_SETTINGS = [
        {
            "key": "clinic.name",
            "value": "Nada Clinic System",
            "value_type": "string",
            "group": "clinic",
            "label": "Clinic name",
            "description": "Full clinic display name.",
            "is_public": True,
            "sort_order": 10,
        },
        {
            "key": "clinic.short_name",
            "value": "Nada Clinic",
            "value_type": "string",
            "group": "clinic",
            "label": "Clinic short name",
            "description": "Short name used in compact UI areas.",
            "is_public": True,
            "sort_order": 20,
        },
        {
            "key": "clinic.phone",
            "value": "",
            "value_type": "string",
            "group": "clinic",
            "label": "Clinic phone",
            "description": "Primary clinic phone number.",
            "is_public": True,
            "sort_order": 30,
        },
        {
            "key": "clinic.whatsapp",
            "value": "",
            "value_type": "string",
            "group": "clinic",
            "label": "Clinic WhatsApp",
            "description": "WhatsApp number for clinic contact.",
            "is_public": True,
            "sort_order": 40,
        },
        {
            "key": "clinic.address",
            "value": "",
            "value_type": "string",
            "group": "clinic",
            "label": "Clinic address",
            "description": "Public clinic address.",
            "is_public": True,
            "sort_order": 50,
        },
        {
            "key": "clinic.logo_path",
            "value": "",
            "value_type": "string",
            "group": "clinic",
            "label": "Logo path",
            "description": "Relative path for clinic logo.",
            "is_public": True,
            "sort_order": 60,
        },
        {
            "key": "clinic.default_doctor_name",
            "value": "Dr. Yahya Zakaria",
            "value_type": "string",
            "group": "clinic",
            "label": "Default doctor name",
            "description": "Default doctor shown in basic clinic settings.",
            "is_public": False,
            "sort_order": 70,
        },
        {
            "key": "localization.timezone",
            "value": "Africa/Cairo",
            "value_type": "string",
            "group": "localization",
            "label": "Timezone",
            "description": "Default system timezone.",
            "is_public": False,
            "sort_order": 110,
        },
        {
            "key": "localization.language",
            "value": "en",
            "value_type": "string",
            "group": "localization",
            "label": "Language",
            "description": "Default system language.",
            "is_public": False,
            "sort_order": 120,
        },
        {
            "key": "localization.date_format",
            "value": "YYYY-MM-DD",
            "value_type": "string",
            "group": "localization",
            "label": "Date format",
            "description": "Default displayed date format.",
            "is_public": False,
            "sort_order": 130,
        },
        {
            "key": "localization.time_format",
            "value": "24h",
            "value_type": "string",
            "group": "localization",
            "label": "Time format",
            "description": "Default displayed time format.",
            "is_public": False,
            "sort_order": 140,
        },
        {
            "key": "appearance.theme",
            "value": "light",
            "value_type": "string",
            "group": "appearance",
            "label": "Theme",
            "description": "Default UI theme.",
            "is_public": False,
            "sort_order": 210,
        },
        {
            "key": "appearance.accent_color",
            "value": "teal",
            "value_type": "string",
            "group": "appearance",
            "label": "Accent color",
            "description": "Default accent color name.",
            "is_public": False,
            "sort_order": 220,
        },
        {
            "key": "appearance.sidebar_density",
            "value": "comfortable",
            "value_type": "string",
            "group": "appearance",
            "label": "Sidebar density",
            "description": "Sidebar spacing preference.",
            "is_public": False,
            "sort_order": 230,
        },
        {
            "key": "workflow.default_landing_page",
            "value": "dashboard",
            "value_type": "string",
            "group": "workflow",
            "label": "Default landing page",
            "description": "Page opened after login.",
            "is_public": False,
            "sort_order": 310,
        },
        {
            "key": "workflow.enable_today_clinic",
            "value": "true",
            "value_type": "boolean",
            "group": "workflow",
            "label": "Enable Today Clinic",
            "description": "Enable Today Clinic workflow later.",
            "is_public": False,
            "sort_order": 320,
        },
        {
            "key": "workflow.enable_patient_workspace",
            "value": "true",
            "value_type": "boolean",
            "group": "workflow",
            "label": "Enable Patient Workspace",
            "description": "Enable patient workspace workflow later.",
            "is_public": False,
            "sort_order": 330,
        },
        {
            "key": "workflow.enable_followup_tracker",
            "value": "true",
            "value_type": "boolean",
            "group": "workflow",
            "label": "Enable Follow-up Tracker",
            "description": "Enable follow-up tracking later.",
            "is_public": False,
            "sort_order": 340,
        },
        {
            "key": "printing.header_enabled",
            "value": "true",
            "value_type": "boolean",
            "group": "printing",
            "label": "Print header enabled",
            "description": "Enable document print header later.",
            "is_public": False,
            "sort_order": 410,
        },
        {
            "key": "printing.footer_enabled",
            "value": "true",
            "value_type": "boolean",
            "group": "printing",
            "label": "Print footer enabled",
            "description": "Enable document print footer later.",
            "is_public": False,
            "sort_order": 420,
        },
        {
            "key": "printing.default_paper_size",
            "value": "A4",
            "value_type": "string",
            "group": "printing",
            "label": "Default paper size",
            "description": "Default paper size for future printing.",
            "is_public": False,
            "sort_order": 430,
        },
        {
            "key": "printing.prescription_template",
            "value": "default",
            "value_type": "string",
            "group": "printing",
            "label": "Prescription template",
            "description": "Default prescription template later.",
            "is_public": False,
            "sort_order": 440,
        },
        {
            "key": "security.session_timeout_minutes",
            "value": "60",
            "value_type": "integer",
            "group": "security",
            "label": "Session timeout minutes",
            "description": "Default session timeout policy.",
            "is_public": False,
            "sort_order": 510,
        },
        {
            "key": "security.require_strong_password",
            "value": "false",
            "value_type": "boolean",
            "group": "security",
            "label": "Require strong password",
            "description": "Reserved for future password policy.",
            "is_public": False,
            "sort_order": 520,
        },
        {
            "key": "security.login_by_phone_enabled",
            "value": "true",
            "value_type": "boolean",
            "group": "security",
            "label": "Login by phone enabled",
            "description": "Allow login using phone if phone exists.",
            "is_public": False,
            "sort_order": 530,
        },
        {
            "key": "system.app_name",
            "value": "Nada Clinic System",
            "value_type": "string",
            "group": "system",
            "label": "Application name",
            "description": "Internal application name.",
            "is_public": True,
            "sort_order": 610,
        },
        {
            "key": "system.stage_label",
            "value": "Stage 1 Settings Foundation",
            "value_type": "string",
            "group": "system",
            "label": "Stage label",
            "description": "Current implementation stage label.",
            "is_public": False,
            "sort_order": 620,
        },
        {
            "key": "system.maintenance_mode",
            "value": "false",
            "value_type": "boolean",
            "group": "system",
            "label": "Maintenance mode",
            "description": "Reserved for future maintenance behavior.",
            "is_public": False,
            "sort_order": 630,
        },
    ]

    @staticmethod
    def get(key, default=None, cast=True):
        setting = Setting.query.filter_by(key=key).first()

        if not setting:
            return default

        if cast:
            return setting.cast_value()

        return setting.value

    @staticmethod
    def set(key, value):
        setting = Setting.query.filter_by(key=key).first()

        if not setting:
            raise ValueError(f"Setting does not exist: {key}")

        if not setting.is_editable:
            raise ValueError(f"Setting is not editable: {key}")

        setting.value = SettingsService.serialize_value(value, setting.value_type)
        db.session.commit()

        return setting

    @staticmethod
    def get_group(group):
        return (
            Setting.query.filter_by(group=group)
            .order_by(Setting.sort_order.asc(), Setting.key.asc())
            .all()
        )

    @staticmethod
    def get_grouped_settings():
        settings = Setting.query.order_by(
            Setting.group.asc(),
            Setting.sort_order.asc(),
            Setting.key.asc(),
        ).all()

        grouped = {}
        for setting in settings:
            grouped.setdefault(setting.group, []).append(setting)

        return grouped

    @staticmethod
    def get_public_settings():
        return {
            setting.key: setting.cast_value()
            for setting in Setting.query.filter_by(is_public=True).all()
        }

    @staticmethod
    def seed_defaults():
        for item in SettingsService.DEFAULT_SETTINGS:
            setting = Setting.query.filter_by(key=item["key"]).first()

            if not setting:
                setting = Setting(**item)
                db.session.add(setting)
                continue

            setting.value_type = item["value_type"]
            setting.group = item["group"]
            setting.label = item["label"]
            setting.description = item["description"]
            setting.is_public = item["is_public"]
            setting.sort_order = item["sort_order"]

        db.session.commit()

    @staticmethod
    def serialize_value(value, value_type):
        if value_type == "boolean":
            return "true" if str(value).lower() in ("1", "true", "yes", "on") else "false"

        if value_type == "integer":
            try:
                return str(int(value))
            except (TypeError, ValueError):
                return "0"

        return "" if value is None else str(value)
