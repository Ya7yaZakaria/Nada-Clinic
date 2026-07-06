from app.extensions import db
from app.models import User


class AuthService:
    """Authentication service."""

    @staticmethod
    def normalize_email(email):
        if not email:
            return None
        return email.strip().lower()

    @staticmethod
    def normalize_phone(phone):
        if not phone:
            return None
        return phone.strip() or None

    @staticmethod
    def find_by_login_identifier(login_identifier):
        identifier = (login_identifier or "").strip()

        if not identifier:
            return None

        if "@" in identifier:
            return User.query.filter_by(email=AuthService.normalize_email(identifier)).first()

        return User.query.filter_by(phone=AuthService.normalize_phone(identifier)).first()

    @staticmethod
    def authenticate(login_identifier, password):
        user = AuthService.find_by_login_identifier(login_identifier)

        if not user:
            return None

        if not user.is_active:
            return None

        if not user.check_password(password):
            return None

        return user

    @staticmethod
    def create_user(email, name, password, phone=None, is_admin_seed=False):
        user = User(
            email=AuthService.normalize_email(email),
            phone=AuthService.normalize_phone(phone),
            name=name.strip(),
            is_admin_seed=is_admin_seed,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user
