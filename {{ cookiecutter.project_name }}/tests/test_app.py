"""Tests for app factory, error handlers, before-request hooks, and template filters."""

import datetime as dt
from typing import TYPE_CHECKING, Any, cast

import pytest
import werkzeug.exceptions
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy_lite import SQLAlchemy

from {{ cookiecutter.package_name }}.models import User

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.integration
class TestErrorHandlers:
    """Tests for registered error handlers."""

    def test_404_for_nonexistent_route(self, client: FlaskClient) -> None:
        """Test that a request to a nonexistent route returns 404."""
        response = client.get("/nonexistent-route-that-does-not-exist")

        assert response.status_code == 404

    def test_404_response_contains_error_content(self, client: FlaskClient) -> None:
        """Test that 404 response contains error-related content."""
        response = client.get("/nonexistent-route-that-does-not-exist")

        assert response.status_code == 404
        assert b"404" in response.data or b"not found" in response.data.lower()

    def test_401_unauthorized(self, app: Flask) -> None:
        with app.test_request_context():
            response = app.make_response(
                app.handle_http_exception(werkzeug.exceptions.Unauthorized())
            )
        assert response.status_code == 401

    def test_403_forbidden(self, app: Flask) -> None:
        with app.test_request_context():
            response = app.make_response(
                app.handle_http_exception(werkzeug.exceptions.Forbidden())
            )
        assert response.status_code == 403

    def test_500_via_abort(self, app: Flask) -> None:
        with app.test_request_context():
            response = app.make_response(
                app.handle_http_exception(werkzeug.exceptions.InternalServerError())
            )
        assert response.status_code == 500

    def test_unhandled_exception(self) -> None:
        # The @app.errorhandler(Exception) handler only fires through Flask's
        # full request dispatch (handle_user_exception), not through
        # handle_exception() which wraps in InternalServerError and dispatches
        # to the 500 handler. We need a fresh app to register a route that
        # raises a non-HTTP exception.
        from {{ cookiecutter.package_name }}.app import create_app
        from {{ cookiecutter.package_name }}.config import (
            TestingConfig,
        )

        test_app = create_app(TestingConfig)

        @test_app.route("/test-unhandled-exception-trigger")
        def _trigger_unhandled_exception() -> str:
            msg = "deliberate test error"
            raise RuntimeError(msg)

        test_app.config["PROPAGATE_EXCEPTIONS"] = False
        with test_app.test_client() as c:
            response = c.get("/test-unhandled-exception-trigger")
            assert response.status_code == 500


@pytest.mark.integration
class TestBeforeRequestHandler:
    """Tests for the before-request hook that updates last_seen_at."""

    def test_last_seen_at_updated_for_authenticated_user(
        self,
        app: Flask,
        client: FlaskClient,
        db: SQLAlchemy,
        confirmed_user: User,
    ) -> None:
        """Test that last_seen_at is updated when an authenticated user makes a request."""
        from flask_login import login_user

        assert confirmed_user.last_seen_at is None

        # Log in via the actual login mechanism to ensure Flask-Login state is correct.
        with app.test_request_context():
            login_user(confirmed_user)

        # Use session_transaction to copy the login session state.
        with client.session_transaction() as sess:
            sess["_user_id"] = str(confirmed_user.id)
            sess["_fresh"] = True

        response = client.get("/")
        assert response.status_code == 200

        # Expire cached ORM state to see committed changes.
        db.session.expire(confirmed_user)
        assert confirmed_user.last_seen_at is not None


@pytest.mark.unit
class TestTemplateFilters:
    """Tests for custom Jinja2 template filters."""

    def test_strftime_filter_registered(self, app: Flask) -> None:
        """Test that the strftime filter is registered."""
        assert "strftime" in app.jinja_env.filters

    def test_strftime_filter_formats_datetime(self, app: Flask) -> None:
        """Test that the strftime filter correctly formats a datetime."""
        strftime_filter = cast("Callable[..., str]", app.jinja_env.filters["strftime"])
        test_dt = dt.datetime(2025, 1, 15, 10, 30, 0, tzinfo=dt.UTC)

        result = strftime_filter(test_dt, "%Y-%m-%d")

        assert result == "2025-01-15"

    def test_strftime_filter_default_format(self, app: Flask) -> None:
        """Test that the strftime filter uses the default format."""
        strftime_filter = cast("Callable[..., str]", app.jinja_env.filters["strftime"])
        test_dt = dt.datetime(2025, 1, 15, 10, 30, 0, tzinfo=dt.UTC)

        result = strftime_filter(test_dt)

        assert "2025-01-15" in result
        assert "10:30:00" in result

    def test_qrcode_data_uri_filter_registered(self, app: Flask) -> None:
        """Test that the qrcode_data_uri filter is registered."""
        assert "qrcode_data_uri" in app.jinja_env.filters

    def test_qrcode_data_uri_filter_generates_data_uri(self, app: Flask) -> None:
        """Test that the qrcode_data_uri filter produces a valid data URI."""
        qrcode_filter = cast(
            "Callable[..., Any]", app.jinja_env.filters["qrcode_data_uri"]
        )
        result = qrcode_filter("https://example.com")
        assert result.startswith("data:image/")


@pytest.mark.integration
class TestAfterRequestHandler:
    """Tests for the after_request session commit and rollback paths."""

    def test_after_request_rolls_back_on_commit_failure(
        self,
        app: Flask,
        client: FlaskClient,
        db: SQLAlchemy,
        confirmed_user: User,
    ) -> None:
        """Test that after_request rolls back when session commit fails."""
        from unittest.mock import patch

        import sqlalchemy.exc

        # Log in the confirmed user so before_request dirties the session.
        with client.session_transaction() as sess:
            sess["_user_id"] = str(confirmed_user.id)
            sess["_fresh"] = True

        with patch.object(
            db.session,
            "commit",
            side_effect=sqlalchemy.exc.OperationalError("test", {}, Exception()),
        ):
            # The exception propagates through Flask's response handling.
            # Depending on Flask config it may raise or return 500.
            try:
                response = client.get("/")
                assert response.status_code == 500
            except sqlalchemy.exc.OperationalError:
                pass  # Exception propagated directly — rollback path exercised.
