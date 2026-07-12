import os

from flask import Flask, render_template

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

    return app


def register_blueprints(app):
    """Register application blueprints."""

    from app.routes.admin import admin_bp
    from app.routes.appointments import appointments_bp
    from app.routes.auth import auth_bp
    from app.routes.drug_settings import drug_settings_bp
    from app.routes.drugs import drugs_bp
    from app.routes.journeys import journeys_bp
    from app.routes.main import main_bp
    from app.routes.patients import patients_bp
    from app.routes.today_clinic import today_clinic_bp
    from app.routes.visits import visits_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(today_clinic_bp)
    app.register_blueprint(drug_settings_bp)
    app.register_blueprint(drugs_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(journeys_bp)
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
