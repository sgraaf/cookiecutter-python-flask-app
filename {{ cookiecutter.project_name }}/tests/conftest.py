"""Test fixtures and configuration."""

from collections.abc import Iterator

import pytest
import sqlalchemy as sa
import sqlalchemy.event
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy_lite import SQLAlchemy

from {{ cookiecutter.package_name }}.app import create_app
from {{ cookiecutter.package_name }}.config import TestingConfig
from {{ cookiecutter.package_name }}.extensions import db as db_obj
from {{ cookiecutter.package_name }}.models import Model, User


@pytest.fixture(scope="session")
def app() -> Flask:
    """Create and configure a Flask application for testing.

    Tables are created once per session.

    The event listeners fix SQLite's broken savepoint handling so that
    :meth:`~flask_sqlalchemy_lite.SQLAlchemy.test_isolation` can roll back
    transactions reliably.
    """
    app = create_app(TestingConfig)

    with app.app_context():
        engine = db_obj.engine

        @sa.event.listens_for(engine, "connect")
        def _set_sqlite_pragma(
            dbapi_connection: sa.Any,
            _connection_record: sa.Any,
        ) -> None:
            dbapi_connection.isolation_level = None

        @sa.event.listens_for(engine, "begin")
        def _do_begin(conn: sa.Connection) -> None:
            conn.exec_driver_sql("BEGIN")

        Model.metadata.create_all(engine)

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def db(app: Flask) -> Iterator[SQLAlchemy]:
    """Provide a transactional database session that rolls back after each test.

    Pushes a fresh app context and ensures that all writes are rolled back
    when the test finishes.
    """
    ctx = app.app_context()
    ctx.push()

    with db_obj.test_isolation():
        yield db_obj

    ctx.pop()


@pytest.fixture
def user(db: SQLAlchemy) -> User:
    """Create an unconfirmed user."""
    return User.create(
        username="testuser",
        email_address="test@example.com",
        password="password123",
    )


@pytest.fixture
def confirmed_user(db: SQLAlchemy) -> User:
    """Create a confirmed and active user."""
    from {{ cookiecutter.package_name }}.utils import utcnow

    return User.create(
        username="confirmeduser",
        email_address="confirmed@example.com",
        password="password123",
        confirmed_at=utcnow(),
    )
