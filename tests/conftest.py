"""Project-wide pytest lifecycle fixtures.

Keep only truly global fixtures here. Domain-specific records stay explicit in
individual tests or in ``tests.factories`` so test setup remains readable.
"""

import pytest

from app.extensions import db
from tests.factories import make_app_server


@pytest.fixture
def app():
    """Standard testing app with a fresh database for one test."""
    application = make_app_server()
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """HTTP client bound to the standard per-test application fixture."""
    return app.test_client()

def pytest_configure(config):
    """Register suite categories used by development and checkpoint runs."""
    config.addinivalue_line(
        "markers",
        "slow: expensive integration coverage kept for checkpoint/full runs",
    )
    config.addinivalue_line(
        "markers",
        "migration: migration/schema compatibility coverage",
    )

