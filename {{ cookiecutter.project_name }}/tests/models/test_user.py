"""Tests for the User ORM model."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from unittest.mock import patch

import pyotp
import pytest

from {{ cookiecutter.package_name }}.models import User

if TYPE_CHECKING:
    from flask import Flask
    from flask_sqlalchemy_lite import SQLAlchemy


@pytest.mark.integration
class TestUserPassword:
    """Tests for User password hashing and verification."""

    def test_reading_password_raises_attribute_error(
        self, app: Flask, user: User
    ) -> None:
        with pytest.raises(AttributeError, match="not a readable attribute"):
            _ = user.password

    def test_setting_password_stores_hash(self, app: Flask, user: User) -> None:
        assert user.password_hash != "password123"
        assert user.password_hash is not None

    def test_verify_password_returns_true_for_correct(
        self, app: Flask, user: User
    ) -> None:
        assert user.verify_password("password123") is True

    def test_verify_password_returns_false_for_wrong(
        self, app: Flask, user: User
    ) -> None:
        assert user.verify_password("wrongpassword") is False


@pytest.mark.integration
class TestUserTOTP:
    """Tests for User TOTP functionality."""

    def test_otp_secret_is_generated(self, app: Flask, user: User) -> None:
        assert user.otp_secret is not None
        assert len(user.otp_secret) > 0

    def test_totp_property_returns_totp_instance(self, app: Flask, user: User) -> None:
        assert isinstance(user.totp, pyotp.TOTP)

    def test_otpauth_uri_contains_email(self, app: Flask, user: User) -> None:
        uri = user.otpauth_uri
        assert "test%40example.com" in uri

    def test_verify_totp_returns_true_for_valid_token(
        self, app: Flask, user: User
    ) -> None:
        current_token = user.totp.now()
        assert user.verify_totp(current_token) is True

    def test_verify_totp_returns_false_for_invalid_token(
        self, app: Flask, user: User
    ) -> None:
        assert user.verify_totp("000000") is False

    def test_verify_totp_rejects_replay(self, app: Flask, user: User) -> None:
        current_token = user.totp.now()
        # first use should succeed
        assert user.verify_totp(current_token) is True
        # same token in the same time window should be rejected (replay)
        assert user.verify_totp(current_token) is False

    def test_verify_totp_accepts_next_window(self, app: Flask, user: User) -> None:
        current_token = user.totp.now()
        assert user.verify_totp(current_token) is True
        # simulate time advancing to the next window
        next_counter = int(time.time()) // user.totp.interval + 1
        next_time = next_counter * user.totp.interval
        next_token = user.totp.at(next_time)
        with patch("cookiecutter_python_flask_app_demo.models.user.time") as mock_time:
            mock_time.time.return_value = float(next_time)
            assert user.verify_totp(next_token) is True


@pytest.mark.integration
class TestUserConfirmationToken:
    """Tests for User confirmation token generation and verification."""

    def test_get_confirmation_token_returns_string(
        self, app: Flask, user: User
    ) -> None:
        token = user.get_confirmation_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_confirmation_token_with_valid_token(
        self, app: Flask, user: User
    ) -> None:
        assert user.is_active is False
        token = user.get_confirmation_token()
        result = User.verify_confirmation_token(token)
        assert result is not None
        assert result.id == user.id
        # verify_confirmation_token only decodes; it does not activate the user
        assert result.is_active is False
        assert result.confirmed_at is None

    def test_verify_confirmation_token_with_invalid_token(
        self, app: Flask, db: SQLAlchemy
    ) -> None:
        result = User.verify_confirmation_token("invalid.token.here")
        assert result is None

    def test_verify_confirmation_token_with_expired_token(
        self, app: Flask, user: User
    ) -> None:
        token = user.get_confirmation_token(expires_in=-1)
        result = User.verify_confirmation_token(token)
        assert result is None


@pytest.mark.integration
class TestUserPasswordResetToken:
    """Tests for User password reset token generation and verification."""

    def test_get_password_reset_token_returns_string(
        self, app: Flask, user: User
    ) -> None:
        token = user.get_password_reset_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_password_reset_token_with_valid_token(
        self, app: Flask, user: User
    ) -> None:
        token = user.get_password_reset_token()
        result = User.verify_password_reset_token(token)
        assert result is not None
        assert result.id == user.id

    def test_verify_password_reset_token_with_invalid_token(
        self, app: Flask, db: SQLAlchemy
    ) -> None:
        result = User.verify_password_reset_token("invalid.token.here")
        assert result is None

    def test_verify_password_reset_token_does_not_activate_user(
        self, app: Flask, user: User
    ) -> None:
        assert user.is_active is False
        token = user.get_password_reset_token()
        User.verify_password_reset_token(token)
        assert user.is_active is False


@pytest.mark.integration
class TestUserIsActive:
    """Tests for User.is_active hybrid property."""

    def test_unconfirmed_user_is_not_active(self, app: Flask, user: User) -> None:
        assert user.confirmed_at is None
        assert user.is_active is False

    def test_confirmed_user_is_active(self, app: Flask, confirmed_user: User) -> None:
        assert confirmed_user.confirmed_at is not None
        assert confirmed_user.is_active is True

    def test_is_active_expression_in_query(
        self, app: Flask, db: SQLAlchemy, confirmed_user: User
    ) -> None:
        """Verify the SQL expression form works in queries."""
        active = User.get_all(User.is_active)
        assert any(u.id == confirmed_user.id for u in active)


@pytest.mark.integration
class TestEmailNormalization:
    """Tests for email address case normalization."""

    def test_email_lowercased_on_create(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="upper",
            email_address="Upper@Example.COM",
            password="password123",
        )
        assert user.email_address == "upper@example.com"

    def test_email_lowercased_on_update(self, app: Flask, user: User) -> None:
        user.update(email_address="NEW@Example.COM")
        assert user.email_address == "new@example.com"


@pytest.mark.integration
class TestUserTokenExpiry:
    """Tests for token expiry edge cases."""

    def test_verify_confirmation_token_with_zero_expiry(
        self, app: Flask, db: SQLAlchemy, user: User
    ) -> None:
        """A confirmation token with zero expiry should be rejected after a short delay."""
        token = user.get_confirmation_token(expires_in=0)
        time.sleep(0.1)
        result = User.verify_confirmation_token(token)
        assert result is None

    def test_verify_password_reset_token_with_zero_expiry(
        self, app: Flask, db: SQLAlchemy, user: User
    ) -> None:
        """A password reset token with zero expiry should be rejected after a short delay."""
        token = user.get_password_reset_token(expires_in=0)
        time.sleep(0.1)
        result = User.verify_password_reset_token(token)
        assert result is None


@pytest.mark.integration
class TestUserOtpauthUri:
    """Tests for TOTP otpauth URI content."""

    def test_otpauth_uri_contains_issuer(
        self, app: Flask, db: SQLAlchemy, user: User
    ) -> None:
        """The otpauth URI should contain the TOTP scheme and the user's email."""
        from urllib.parse import quote

        uri = user.otpauth_uri
        assert "otpauth://totp/" in uri
        assert quote(user.email_address, safe="") in uri


@pytest.mark.integration
class TestUserPasswordEdgeCases:
    """Tests for password verification edge cases."""

    def test_password_hash_is_not_plaintext(
        self, app: Flask, db: SQLAlchemy, user: User
    ) -> None:
        """The stored password hash must not equal the plaintext password."""
        assert user.password_hash != "password123"

    def test_verify_password_with_empty_string(
        self, app: Flask, db: SQLAlchemy, user: User
    ) -> None:
        """Verifying an empty string should return False."""
        assert user.verify_password("") is False

    def test_verify_password_with_none_raises(
        self, app: Flask, db: SQLAlchemy, user: User
    ) -> None:
        """Verifying None should raise AttributeError from werkzeug."""
        with pytest.raises(AttributeError):
            user.verify_password(None)  # type: ignore[arg-type]
