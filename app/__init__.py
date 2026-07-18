import os

from flask import Flask, render_template
from flask_login import current_user

from app.commands import register_commands
from app.config import config_by_name
from app.extensions import init_extensions


def create_app(config_name=None):
    """Application factory for Nada Clinic System."""

    app = Flask(__name__)

    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    init_extensions(app)

    from app import models  # noqa: F401

    register_blueprints(app)
    register_error_handlers(app)
    register_commands(app)
    register_context_processors(app)

    return app


def register_context_processors(app):
    """Register template context helpers for global UI preferences."""

    @app.context_processor
    def inject_ui_preferences():
        defaults = {
            "theme": "light",
            "bootstrap_theme": "light",
            "language": "en",
            "direction": "ltr",
            "accent_color": "teal",
            "font_size": "normal",
            "sidebar_density": "comfortable",
            "card_density": "comfortable",
            "table_density": "comfortable",
        }
        default_clinic_profile = {
            "name": "Nada Clinic System",
            "short_name": "Nada Clinic",
            "phone": "",
            "whatsapp": "",
            "address": "",
            "logo_path": "",
            "default_doctor_name": "",
        }

        try:
            from app.services.settings_service import SettingsService

            ui_preferences = SettingsService.get_ui_preferences()
            clinic_profile = SettingsService.get_clinic_profile()
        except Exception:
            ui_preferences = defaults
            clinic_profile = default_clinic_profile

        dev_role_preview = {
            "enabled": False,
            "active": False,
            "preview_role": None,
            "available_roles": (),
            "actual_roles": [],
            "effective_roles": [],
        }

        try:
            from app.services.development_role_preview_service import (
                DevelopmentRolePreviewService,
            )

            dev_role_preview = (
                DevelopmentRolePreviewService
                .template_context(current_user)
            )
        except Exception:
            pass

        return {
            "dev_role_preview": dev_role_preview,
            "ui_preferences": ui_preferences,
            "ui_theme": ui_preferences.get("theme", defaults["theme"]),
            "ui_bootstrap_theme": ui_preferences.get("bootstrap_theme", defaults["bootstrap_theme"]),
            "ui_language": ui_preferences.get("language", defaults["language"]),
            "ui_direction": ui_preferences.get("direction", defaults["direction"]),
            "ui_accent": ui_preferences.get("accent_color", defaults["accent_color"]),
            "ui_font_size": ui_preferences.get("font_size", defaults["font_size"]),
            "ui_sidebar_density": ui_preferences.get("sidebar_density", defaults["sidebar_density"]),
            "ui_card_density": ui_preferences.get("card_density", defaults["card_density"]),
            "ui_table_density": ui_preferences.get("table_density", defaults["table_density"]),
            "clinic_profile": clinic_profile,
            "clinic_name": clinic_profile.get("name", default_clinic_profile["name"]),
            "clinic_short_name": clinic_profile.get("short_name", default_clinic_profile["short_name"]),
            "clinic_phone": clinic_profile.get("phone", default_clinic_profile["phone"]),
            "clinic_whatsapp": clinic_profile.get("whatsapp", default_clinic_profile["whatsapp"]),
            "clinic_address": clinic_profile.get("address", default_clinic_profile["address"]),
            "clinic_logo_path": clinic_profile.get("logo_path", default_clinic_profile["logo_path"]),
            "clinic_default_doctor_name": clinic_profile.get(
                "default_doctor_name",
                default_clinic_profile["default_doctor_name"],
            ),
        }


def register_blueprints(app):
    """Register application blueprints."""

    from app.routes.admin import admin_bp
    from app.routes.appointments import appointments_bp
    from app.routes.auth import auth_bp
    from app.routes.drug_settings import drug_settings_bp
    from app.routes.documents import documents_bp
    from app.routes.development import development_bp
    from app.routes.finance import finance_bp
    from app.routes.drugs import drugs_bp
    from app.routes.investigation_presets import investigation_presets_bp
    from app.routes.investigations import investigations_bp
    from app.routes.journeys import journeys_bp
    from app.routes.main import main_bp
    from app.routes.patients import patients_bp
    from app.routes.partners import partners_bp
    from app.routes.prescription_presets import prescription_presets_bp
    from app.routes.print_templates import print_templates_bp
    from app.routes.settings import settings_bp
    from app.routes.today_clinic import today_clinic_bp
    from app.routes.ultrasounds import ultrasounds_bp
    from app.routes.surgeries import surgeries_bp
    from app.routes.visits import visits_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(today_clinic_bp)
    app.register_blueprint(drug_settings_bp)
    app.register_blueprint(drugs_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(development_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(prescription_presets_bp)
    app.register_blueprint(print_templates_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(partners_bp)
    app.register_blueprint(investigations_bp)
    app.register_blueprint(investigation_presets_bp)
    app.register_blueprint(journeys_bp)
    app.register_blueprint(ultrasounds_bp)
    app.register_blueprint(surgeries_bp)
    app.register_blueprint(visits_bp)
    app.register_blueprint(main_bp)


def register_error_handlers(app):
    """Register basic error pages."""

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500
