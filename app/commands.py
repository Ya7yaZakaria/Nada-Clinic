import os

import click

from app.extensions import db
from app.models import User
from app.services.auth_service import AuthService


def register_commands(app):
    """Register custom Flask CLI commands."""

    @app.cli.command("seed-admin")
    def seed_admin():
        """Create the first local admin seed user from .env."""

        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        name = os.getenv("ADMIN_NAME", "Clinic Admin")
        phone = os.getenv("ADMIN_PHONE") or None

        if not email or not password:
            raise click.ClickException(
                "ADMIN_EMAIL and ADMIN_PASSWORD must be set in .env."
            )

        existing_user = User.query.filter_by(
            email=AuthService.normalize_email(email)
        ).first()

        if existing_user:
            click.echo(f"Admin seed already exists: {existing_user.email}")
            return

        user = AuthService.create_user(
            email=email,
            name=name,
            password=password,
            phone=phone,
            is_admin_seed=True,
        )

        db.session.commit()
        click.echo(f"Admin seed created: {user.email}")
