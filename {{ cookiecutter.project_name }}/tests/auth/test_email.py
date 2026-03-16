"""Tests for authentication email functions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from {{ cookiecutter.package_name }}.auth.email import (
    send_confirmation_email,
    send_password_reset_email,
)

if TYPE_CHECKING:
    from flask import Flask

    from {{ cookiecutter.package_name }}.models import User


@pytest.mark.integration
class TestSendConfirmationEmail:
    """Tests for send_confirmation_email."""

    @patch("{{ cookiecutter.package_name }}.auth.email.send_email")
    @patch("{{ cookiecutter.package_name }}.auth.email.render_template")
    def test_calls_send_email_with_confirm_subject(
        self,
        mock_render: MagicMock,
        mock_send_email: MagicMock,
        app: Flask,
        confirmed_user: User,
    ) -> None:
        mock_render.return_value = "rendered"
        send_confirmation_email(confirmed_user)
        mock_send_email.assert_called_once()
        assert "Confirm" in mock_send_email.call_args.kwargs["subject"]

    @patch("{{ cookiecutter.package_name }}.auth.email.send_email")
    @patch("{{ cookiecutter.package_name }}.auth.email.render_template")
    def test_uses_user_email_as_recipient(
        self,
        mock_render: MagicMock,
        mock_send_email: MagicMock,
        app: Flask,
        confirmed_user: User,
    ) -> None:
        mock_render.return_value = "rendered"
        send_confirmation_email(confirmed_user)
        assert mock_send_email.call_args.kwargs["recipients"] == [
            confirmed_user.email_address
        ]

    @patch("{{ cookiecutter.package_name }}.auth.email.send_email")
    @patch("{{ cookiecutter.package_name }}.auth.email.render_template")
    def test_passes_rendered_templates_as_bodies(
        self,
        mock_render: MagicMock,
        mock_send_email: MagicMock,
        app: Flask,
        confirmed_user: User,
    ) -> None:
        mock_render.side_effect = ["text_body", "html_body"]
        send_confirmation_email(confirmed_user)
        kwargs = mock_send_email.call_args.kwargs
        assert kwargs["text_body"] == "text_body"
        assert kwargs["html_body"] == "html_body"


@pytest.mark.integration
class TestSendPasswordResetEmail:
    """Tests for send_password_reset_email."""

    @patch("{{ cookiecutter.package_name }}.auth.email.send_email")
    @patch("{{ cookiecutter.package_name }}.auth.email.render_template")
    def test_calls_send_email_with_reset_subject(
        self,
        mock_render: MagicMock,
        mock_send_email: MagicMock,
        app: Flask,
        confirmed_user: User,
    ) -> None:
        mock_render.return_value = "rendered"
        send_password_reset_email(confirmed_user)
        mock_send_email.assert_called_once()
        assert "Reset" in mock_send_email.call_args.kwargs["subject"]

    @patch("{{ cookiecutter.package_name }}.auth.email.send_email")
    @patch("{{ cookiecutter.package_name }}.auth.email.render_template")
    def test_uses_user_email_as_recipient(
        self,
        mock_render: MagicMock,
        mock_send_email: MagicMock,
        app: Flask,
        confirmed_user: User,
    ) -> None:
        mock_render.return_value = "rendered"
        send_password_reset_email(confirmed_user)
        assert mock_send_email.call_args.kwargs["recipients"] == [
            confirmed_user.email_address
        ]

    @patch("{{ cookiecutter.package_name }}.auth.email.send_email")
    @patch("{{ cookiecutter.package_name }}.auth.email.render_template")
    def test_passes_rendered_templates_as_bodies(
        self,
        mock_render: MagicMock,
        mock_send_email: MagicMock,
        app: Flask,
        confirmed_user: User,
    ) -> None:
        mock_render.side_effect = ["text_body", "html_body"]
        send_password_reset_email(confirmed_user)
        kwargs = mock_send_email.call_args.kwargs
        assert kwargs["text_body"] == "text_body"
        assert kwargs["html_body"] == "html_body"
