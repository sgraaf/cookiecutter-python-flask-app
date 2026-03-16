"""Tests for auth views."""

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy_lite import SQLAlchemy

from {{ cookiecutter.package_name }}.models import User


@pytest.fixture(autouse=True)
def _disable_csrf(app: Flask) -> Iterator[None]:
    app.config["WTF_CSRF_ENABLED"] = False
    yield
    app.config["WTF_CSRF_ENABLED"] = True


def _login(client: FlaskClient, user: User) -> None:
    """Log in a user by injecting the session cookie."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)


@pytest.mark.integration
class TestRegister:
    """Tests for the registration view."""

    def test_get_returns_200(self, client: FlaskClient, db: SQLAlchemy) -> None:
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Register" in response.data

    @patch("{{ cookiecutter.package_name }}.auth.views.send_confirmation_email")
    def test_post_valid_creates_user_and_redirects(
        self, mock_send: object, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        response = client.post(
            "/auth/register",
            data={
                "email_address": "newuser@example.com",
                "password": "securepass",
                "username": "newuser",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"A confirmation email has been sent" in response.data
        assert User.get_by(email_address="newuser@example.com") is not None

    def test_post_duplicate_email_shows_error(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        User.create(
            username="existing",
            email_address="dup@example.com",
            password="password123",
        )
        response = client.post(
            "/auth/register",
            data={
                "email_address": "dup@example.com",
                "password": "securepass",
                "username": "another",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"already exists an account using this email" in response.data

    def test_post_duplicate_username_shows_error(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        User.create(
            username="taken",
            email_address="taken@example.com",
            password="password123",
        )
        response = client.post(
            "/auth/register",
            data={
                "email_address": "different@example.com",
                "password": "securepass",
                "username": "taken",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"already exists an account this username" in response.data

    def test_authenticated_user_redirects_to_index(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.get("/auth/register", follow_redirects=False)
        assert response.status_code == 302
        assert "/index" in response.location


@pytest.mark.integration
class TestConfirmation:
    """Tests for the email confirmation view."""

    def test_valid_token_confirms_user(
        self, client: FlaskClient, db: SQLAlchemy, user: User
    ) -> None:
        token = user.get_confirmation_token()
        response = client.get(f"/auth/confirmation/{token}", follow_redirects=True)
        assert response.status_code == 200
        assert b"Your email address is confirmed" in response.data

    def test_invalid_token_flashes_error(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        response = client.get("/auth/confirmation/invalid-token", follow_redirects=True)
        assert response.status_code == 200
        assert b"invalid or has expired" in response.data

    def test_authenticated_user_redirects_to_index(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        token = confirmed_user.get_confirmation_token()
        response = client.get(f"/auth/confirmation/{token}", follow_redirects=False)
        assert response.status_code == 302
        assert "/index" in response.location


@pytest.mark.integration
class TestLogin:
    """Tests for the login view."""

    def test_get_returns_200(self, client: FlaskClient, db: SQLAlchemy) -> None:
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_post_valid_credentials_redirects(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        response = client.post(
            "/auth/login",
            data={
                "email_address": "confirmed@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/index" in response.location

    def test_post_wrong_password_shows_error(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        response = client.post(
            "/auth/login",
            data={
                "email_address": "confirmed@example.com",
                "password": "wrongpassword",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid email address or password" in response.data

    def test_post_nonexistent_email_shows_error(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        response = client.post(
            "/auth/login",
            data={
                "email_address": "nobody@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid email address or password" in response.data

    def test_post_unconfirmed_user_shows_error(
        self, client: FlaskClient, db: SQLAlchemy, user: User
    ) -> None:
        response = client.post(
            "/auth/login",
            data={
                "email_address": "test@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"First confirm your email address" in response.data

    def test_authenticated_user_redirects_to_index(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.get("/auth/login", follow_redirects=False)
        assert response.status_code == 302
        assert "/index" in response.location

    def test_login_with_next_param_redirects(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        response = client.post(
            "/auth/login?next=/auth/two-factor/setup",
            data={
                "email_address": "confirmed@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/auth/two-factor/setup" in response.location

    def test_login_with_external_next_redirects_to_index(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        response = client.post(
            "/auth/login?next=http://evil.com/steal",
            data={
                "email_address": "confirmed@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/index" in response.location
        assert "evil.com" not in response.location

    def test_login_otp_enabled_redirects_to_two_factor(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        confirmed_user.update(otp_enabled=True)
        response = client.post(
            "/auth/login",
            data={
                "email_address": "confirmed@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/auth/two-factor" in response.location


@pytest.mark.integration
class TestTwoFactor:
    """Tests for the two-factor authentication view."""

    def test_redirects_to_login_without_session(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        response = client.get("/auth/two-factor", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_valid_totp_logs_in(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        confirmed_user.update(otp_enabled=True)
        valid_token = confirmed_user.totp.now()
        with client.session_transaction() as sess:
            sess["user_id"] = confirmed_user.id
            sess["remember_me"] = False
        response = client.post(
            "/auth/two-factor",
            data={"token": valid_token},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/index" in response.location

    def test_invalid_totp_shows_error(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        confirmed_user.update(otp_enabled=True)
        with client.session_transaction() as sess:
            sess["user_id"] = confirmed_user.id
            sess["remember_me"] = False
        response = client.post(
            "/auth/two-factor",
            data={"token": "000000"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid token" in response.data

    def test_authenticated_user_redirects_to_index(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.get("/auth/two-factor", follow_redirects=False)
        assert response.status_code == 302
        assert "/index" in response.location

    def test_user_not_found_redirects_to_login(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        with client.session_transaction() as sess:
            sess["user_id"] = 99999
            sess["remember_me"] = False
        response = client.post(
            "/auth/two-factor",
            data={"token": "000000"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Something went wrong during two-factor authentication" in response.data

    def test_get_renders_form(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        confirmed_user.update(otp_enabled=True)
        with client.session_transaction() as sess:
            sess["user_id"] = confirmed_user.id
            sess["remember_me"] = False
        response = client.get("/auth/two-factor")
        assert response.status_code == 200


@pytest.mark.integration
class TestLogout:
    """Tests for the logout view."""

    def test_logout_redirects_to_index(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.get("/auth/logout", follow_redirects=False)
        assert response.status_code == 302
        assert "/index" in response.location


@pytest.mark.integration
class TestPasswordResetRequest:
    """Tests for the password reset request view."""

    def test_get_returns_200(self, client: FlaskClient, db: SQLAlchemy) -> None:
        response = client.get("/auth/password-reset")
        assert response.status_code == 200

    @patch("{{ cookiecutter.package_name }}.auth.views.send_password_reset_email")
    def test_post_valid_email_shows_check_inbox(
        self,
        mock_send: object,
        client: FlaskClient,
        db: SQLAlchemy,
        confirmed_user: User,
    ) -> None:
        response = client.post(
            "/auth/password-reset",
            data={"email_address": "confirmed@example.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Check your inbox" in response.data

    def test_post_nonexistent_email_still_shows_check_inbox(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        response = client.post(
            "/auth/password-reset",
            data={"email_address": "nobody@example.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Check your inbox" in response.data

    def test_authenticated_user_redirects_to_index(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.get("/auth/password-reset", follow_redirects=False)
        assert response.status_code == 302
        assert "/index" in response.location


@pytest.mark.integration
class TestPasswordResetConfirmation:
    """Tests for the password reset confirmation view."""

    def test_get_valid_token_returns_200(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        token = confirmed_user.get_password_reset_token()
        response = client.get(f"/auth/password-reset/{token}")
        assert response.status_code == 200

    def test_post_valid_token_resets_password(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        token = confirmed_user.get_password_reset_token()
        response = client.post(
            f"/auth/password-reset/{token}",
            data={"password": "newsecurepass"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Your password has been reset" in response.data
        # Verify new password works
        updated_user = User.get_by(id=confirmed_user.id)
        assert updated_user is not None
        assert updated_user.verify_password("newsecurepass")

    def test_invalid_token_redirects_to_index(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        response = client.get(
            "/auth/password-reset/invalid-token", follow_redirects=False
        )
        assert response.status_code == 302
        assert "/index" in response.location

    def test_authenticated_user_redirects_to_index(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        token = confirmed_user.get_password_reset_token()
        response = client.get(f"/auth/password-reset/{token}", follow_redirects=False)
        assert response.status_code == 302
        assert "/index" in response.location


@pytest.mark.integration
class TestAuthenticate:
    """Tests for the authenticate view."""

    def test_get_password_form_without_otp(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.get("/auth/authenticate")
        assert response.status_code == 200

    def test_post_valid_password_confirms_login(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.post(
            "/auth/authenticate",
            data={"password": "password123"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/index" in response.location

    def test_post_invalid_password_shows_error(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.post(
            "/auth/authenticate",
            data={"password": "wrongpassword"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid password" in response.data

    def test_get_totp_form_with_otp_enabled(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        confirmed_user.update(otp_enabled=True)
        _login(client, confirmed_user)
        response = client.get("/auth/authenticate")
        assert response.status_code == 200

    def test_post_valid_totp_confirms_login(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        confirmed_user.update(otp_enabled=True)
        _login(client, confirmed_user)
        valid_token = confirmed_user.totp.now()
        response = client.post(
            "/auth/authenticate",
            data={"token": valid_token},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/index" in response.location

    def test_post_invalid_totp_shows_error(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        confirmed_user.update(otp_enabled=True)
        _login(client, confirmed_user)
        response = client.post(
            "/auth/authenticate",
            data={"token": "000000"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid token" in response.data


@pytest.mark.integration
class TestTwoFactorSetup:
    """Tests for the two-factor setup view."""

    def test_get_returns_200_with_cache_headers(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.get("/auth/two-factor/setup")
        assert response.status_code == 200
        assert (
            response.headers["Cache-Control"] == "no-cache, no-store, must-revalidate"
        )
        assert response.headers["Pragma"] == "no-cache"
        assert response.headers["Expires"] == "0"

    def test_post_valid_totp_enables_otp(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        valid_token = confirmed_user.totp.now()
        response = client.post(
            "/auth/two-factor/setup",
            data={"token": valid_token},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/index" in response.location
        updated = User.get_by(id=confirmed_user.id)
        assert updated is not None
        assert updated.otp_enabled is True

    def test_post_invalid_totp_shows_error(
        self, client: FlaskClient, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        _login(client, confirmed_user)
        response = client.post(
            "/auth/two-factor/setup",
            data={"token": "000000"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid token, please try again" in response.data

    def test_unauthenticated_redirects(
        self, client: FlaskClient, db: SQLAlchemy
    ) -> None:
        response = client.get("/auth/two-factor/setup", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.location
