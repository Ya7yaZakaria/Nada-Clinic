import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///nada_clinic.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = os.getenv("WTF_CSRF_ENABLED", "True").lower() == "true"
    DEV_ROLE_PREVIEW_ENABLED = False
    DEV_ROLE_PREVIEW_EMAILS = ""


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    DEV_ROLE_PREVIEW_ENABLED = (
        os.getenv(
            "DEV_ROLE_PREVIEW_ENABLED",
            "True",
        ).lower()
        == "true"
    )
    DEV_ROLE_PREVIEW_EMAILS = os.getenv(
        "DEV_ROLE_PREVIEW_EMAILS",
        "",
    )


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
