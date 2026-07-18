import os

import click

from app.extensions import db
from app.models import User
from app.services.auth_service import AuthService
from app.services.demo_data_service import DemoDataService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService


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

    @app.cli.command("seed-rbac")
    def seed_rbac():
        """Seed system roles, permissions, and first admin roles."""

        RBACService.seed_roles_permissions()

        admin_email = os.getenv("ADMIN_EMAIL")
        if admin_email:
            try:
                user = RBACService.assign_admin_seed_roles(admin_email)
                click.echo(f"RBAC seeded. Admin roles assigned to: {user.email}")
                return
            except ValueError:
                click.echo("RBAC seeded. Admin user not found yet.")

        click.echo("RBAC seeded.")

    @app.cli.command("seed-settings")
    def seed_settings():
        """Seed default clinic/system settings."""

        SettingsService.seed_defaults()
        click.echo("Default settings seeded.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Create five months of realistic local clinic demo data."""
        if not (app.debug or app.testing):
            raise click.ClickException(
                "seed-demo is available only in development or testing."
            )

        try:
            result = DemoDataService.seed()
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc

        summary = DemoDataService.summary()

        click.echo(result["message"])
        click.echo(
            "Period: "
            f'{summary["period_start"]} to '
            f'{summary["period_end"]}'
        )
        click.echo(f'Patients: {summary["patients"]}')
        click.echo(f'Appointments: {summary["appointments"]}')
        click.echo(f'Visits: {summary["visits"]}')
        click.echo(f'Journeys: {summary["journeys"]}')
        click.echo(f'Partners: {summary["partners"]}')
        click.echo(
            f'Prescriptions: {summary["prescriptions"]}'
        )
        click.echo(
            "Investigation results: "
            f'{summary["investigation_results"]}'
        )
        click.echo(
            "Clinic ultrasounds: "
            f'{summary["clinic_ultrasounds"]}'
        )
        click.echo(
            "External ultrasounds: "
            f'{summary["external_ultrasounds"]}'
        )
        click.echo(f'Documents: {summary["documents"]}')
        click.echo(f'Surgeries: {summary["surgeries"]}')
        click.echo(
            f'Finance charges: {summary["finance_charges"]}'
        )
        click.echo(f'Expenses: {summary["expenses"]}')
        click.echo("No users were created.")
