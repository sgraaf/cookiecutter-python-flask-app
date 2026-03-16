"""Tests for authentication forms."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from werkzeug.datastructures import MultiDict

from {{ cookiecutter.package_name }}.auth.forms import (
    LoginForm,
    PasswordAuthenticationForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    RegistrationForm,
    TwoFactorAuthenticationForm,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from flask import Flask
    from flask_sqlalchemy_lite import SQLAlchemy

    from {{ cookiecutter.package_name }}.models import User


@pytest.fixture(autouse=True)
def _disable_csrf(app: Flask) -> Iterator[None]:
    app.config["WTF_CSRF_ENABLED"] = False
    yield
    app.config["WTF_CSRF_ENABLED"] = True


# ---------------------------------------------------------------------------
# RegistrationForm
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestRegistrationForm:
    """Tests for RegistrationForm validation."""

    def _make_form(self, **overrides: str) -> RegistrationForm:
        defaults = {
            "email_address": "new@example.com",
            "password": "securepassword",
            "username": "validuser",
        }
        defaults.update(overrides)
        return RegistrationForm(MultiDict(defaults))

    def test_valid_data(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form()
            assert form.validate() is True

    def test_missing_email(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form(email_address="")
            assert form.validate() is False
            assert "email_address" in form.errors

    def test_missing_password(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form(password="")
            assert form.validate() is False
            assert "password" in form.errors

    def test_missing_username(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form(username="")
            assert form.validate() is False
            assert "username" in form.errors

    def test_duplicate_email(self, app: Flask, user: User) -> None:
        with app.test_request_context():
            form = self._make_form(email_address=user.email_address)
            assert form.validate() is False
            assert "email_address" in form.errors
            assert any("already exists" in e for e in form.errors["email_address"])

    def test_duplicate_username(self, app: Flask, user: User) -> None:
        with app.test_request_context():
            form = self._make_form(username=user.username)
            assert form.validate() is False
            assert "username" in form.errors
            assert any("already exists" in e for e in form.errors["username"])

    def test_invalid_email_format(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form(email_address="not-an-email")
            assert form.validate() is False
            assert "email_address" in form.errors

    def test_username_invalid_chars(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form(username="bad user!")
            assert form.validate() is False
            assert "username" in form.errors

    def test_password_too_short(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form(password="short")
            assert form.validate() is False
            assert "password" in form.errors

    def test_username_max_length_boundary(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form(username="a" * 64)
            assert form.validate() is True

    def test_username_too_long(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form(username="a" * 65)
            assert form.validate() is False
            assert "username" in form.errors

    def test_password_min_length_boundary(self, app: Flask, db: SQLAlchemy) -> None:
        with app.test_request_context():
            form = self._make_form(password="a" * 8)
            assert form.validate() is True


# ---------------------------------------------------------------------------
# LoginForm
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLoginForm:
    """Tests for LoginForm validation."""

    def test_valid_data(self, app: Flask) -> None:
        with app.test_request_context():
            form = LoginForm(
                MultiDict({"email_address": "user@example.com", "password": "secret"})
            )
            assert form.validate() is True

    def test_missing_email(self, app: Flask) -> None:
        with app.test_request_context():
            form = LoginForm(MultiDict({"email_address": "", "password": "secret"}))
            assert form.validate() is False
            assert "email_address" in form.errors

    def test_missing_password(self, app: Flask) -> None:
        with app.test_request_context():
            form = LoginForm(
                MultiDict({"email_address": "user@example.com", "password": ""})
            )
            assert form.validate() is False
            assert "password" in form.errors

    def test_invalid_email_format(self, app: Flask) -> None:
        with app.test_request_context():
            form = LoginForm(
                MultiDict({"email_address": "not-an-email", "password": "secret"})
            )
            assert form.validate() is False
            assert "email_address" in form.errors


# ---------------------------------------------------------------------------
# TwoFactorAuthenticationForm
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTwoFactorAuthenticationForm:
    """Tests for TwoFactorAuthenticationForm validation."""

    def test_valid_token(self, app: Flask) -> None:
        with app.test_request_context():
            form = TwoFactorAuthenticationForm(MultiDict({"token": "123456"}))
            assert form.validate() is True

    def test_token_too_short(self, app: Flask) -> None:
        with app.test_request_context():
            form = TwoFactorAuthenticationForm(MultiDict({"token": "123"}))
            assert form.validate() is False
            assert "token" in form.errors

    def test_token_too_long(self, app: Flask) -> None:
        with app.test_request_context():
            form = TwoFactorAuthenticationForm(MultiDict({"token": "1234567"}))
            assert form.validate() is False
            assert "token" in form.errors

    def test_missing_token(self, app: Flask) -> None:
        with app.test_request_context():
            form = TwoFactorAuthenticationForm(MultiDict({"token": ""}))
            assert form.validate() is False
            assert "token" in form.errors


# ---------------------------------------------------------------------------
# PasswordResetForm
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPasswordResetForm:
    """Tests for PasswordResetForm validation."""

    def test_valid_password(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordResetForm(MultiDict({"password": "newpassword123"}))
            assert form.validate() is True

    def test_missing_password(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordResetForm(MultiDict({"password": ""}))
            assert form.validate() is False
            assert "password" in form.errors

    def test_password_too_short(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordResetForm(MultiDict({"password": "short"}))
            assert form.validate() is False
            assert "password" in form.errors

    def test_password_min_length_boundary(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordResetForm(MultiDict({"password": "a" * 8}))
            assert form.validate() is True

    def test_password_max_length_boundary(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordResetForm(MultiDict({"password": "a" * 128}))
            assert form.validate() is True

    def test_password_too_long(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordResetForm(MultiDict({"password": "a" * 129}))
            assert form.validate() is False
            assert "password" in form.errors


# ---------------------------------------------------------------------------
# PasswordResetRequestForm
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPasswordResetRequestForm:
    """Tests for PasswordResetRequestForm validation."""

    def test_valid_email(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordResetRequestForm(
                MultiDict({"email_address": "user@example.com"})
            )
            assert form.validate() is True

    def test_missing_email(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordResetRequestForm(MultiDict({"email_address": ""}))
            assert form.validate() is False
            assert "email_address" in form.errors

    def test_invalid_email_format(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordResetRequestForm(
                MultiDict({"email_address": "not-an-email"})
            )
            assert form.validate() is False
            assert "email_address" in form.errors


# ---------------------------------------------------------------------------
# PasswordAuthenticationForm
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPasswordAuthenticationForm:
    """Tests for PasswordAuthenticationForm validation."""

    def test_valid_password(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordAuthenticationForm(MultiDict({"password": "secret"}))
            assert form.validate() is True

    def test_missing_password(self, app: Flask) -> None:
        with app.test_request_context():
            form = PasswordAuthenticationForm(MultiDict({"password": ""}))
            assert form.validate() is False
            assert "password" in form.errors
