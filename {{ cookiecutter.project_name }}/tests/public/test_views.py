"""Tests for public viewss."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flask.testing import FlaskClient

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from flask_sqlalchemy_lite import SQLAlchemy

    from {{ cookiecutter.package_name }}.models import User


class TestPublicViews:
    """Tests for public viewss."""

    @pytest.mark.unit
    def test_index(self, client: FlaskClient) -> None:
        """Test GET request to index page."""
        response = client.get("/")

        assert response.status_code == 200
        assert b"{{ cookiecutter.friendly_name }}" in response.data

    @pytest.mark.unit
    def test_index_alternate_route(self, client: FlaskClient) -> None:
        """Test GET request to /index also returns 200."""
        response = client.get("/index")

        assert response.status_code == 200
        assert b"{{ cookiecutter.friendly_name }}" in response.data

    @pytest.mark.integration
    @pytest.mark.usefixtures("db")
    def test_users_page_empty(self, client: FlaskClient) -> None:
        """Test GET /users with no users in the database."""
        response = client.get("/users")

        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.usefixtures("db", "confirmed_user")
    def test_users_page_with_users(self, client: FlaskClient) -> None:
        """Test GET /users shows existing users."""
        response = client.get("/users")

        assert response.status_code == 200
        assert b"confirmeduser" in response.data

    @pytest.mark.integration
    @pytest.mark.usefixtures("db", "confirmed_user")
    def test_user_detail_page(self, client: FlaskClient) -> None:
        """Test GET /users/<name> for an existing user."""
        response = client.get("/users/confirmeduser")

        assert response.status_code == 200
        assert b"confirmeduser" in response.data

    @pytest.mark.integration
    @pytest.mark.usefixtures("db")
    def test_user_detail_not_found(self, client: FlaskClient) -> None:
        """Test GET /users/<name> for a nonexistent user returns 404."""
        response = client.get("/users/nonexistent")

        assert response.status_code == 404

    @pytest.mark.unit
    def test_robots_txt(self, client: FlaskClient) -> None:
        """Test GET /robots.txt returns 200."""
        response = client.get("/robots.txt")

        assert response.status_code == 200

    @pytest.mark.unit
    def test_favicon_svg(self, client: FlaskClient) -> None:
        """Test GET /favicon.svg returns 200."""
        response = client.get("/favicon.svg")

        assert response.status_code == 200

    @pytest.mark.unit
    def test_favicon_png(self, client: FlaskClient) -> None:
        """Test GET /favicon.png returns 200."""
        response = client.get("/favicon.png")

        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.usefixtures("db")
    def test_user_detail_for_nonexistent_unicode_username(
        self, client: FlaskClient
    ) -> None:
        """Test GET /users/<name> with a Unicode username returns 404."""
        response = client.get("/users/日本語")

        assert response.status_code == 404


@pytest.mark.integration
class TestNavigation:
    """Tests for navigation links based on auth state."""

    def test_anonymous_user_sees_login_and_register(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        response = client.get("/")
        assert b"Login" in response.data
        assert b"Register" in response.data
        assert b"Logout" not in response.data

    def test_authenticated_user_sees_logout_and_profile(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(confirmed_user.id)
        response = client.get("/")
        assert b"Logout" in response.data
        assert b"confirmeduser" in response.data
        assert b"Login" not in response.data
        assert b"Register" not in response.data
