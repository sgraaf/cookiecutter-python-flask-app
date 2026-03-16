"""Tests for core email utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from {{ cookiecutter.package_name }}.email import send_async_email, send_email

if TYPE_CHECKING:
    from flask import Flask


@pytest.mark.unit
class TestSendEmail:
    """Tests for send_email."""

    @patch("{{ cookiecutter.package_name }}.email.Thread")
    def test_creates_and_starts_thread(
        self, mock_thread_cls: MagicMock, app: Flask
    ) -> None:
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        with app.app_context():
            send_email(
                subject="Test",
                recipients=["a@b.com"],
                text_body="hello",
                html_body="<p>hello</p>",
            )

        mock_thread_cls.assert_called_once()
        mock_thread.start.assert_called_once()

    @patch("{{ cookiecutter.package_name }}.email.Thread")
    def test_thread_target_is_send_async_email(
        self, mock_thread_cls: MagicMock, app: Flask
    ) -> None:
        with app.app_context():
            send_email(
                subject="Test",
                recipients=["a@b.com"],
                text_body="hello",
                html_body="<p>hello</p>",
            )

        call_kwargs = mock_thread_cls.call_args
        assert call_kwargs.kwargs["target"] is send_async_email


@pytest.mark.unit
class TestSendAsyncEmail:
    """Tests for send_async_email."""

    @patch("{{ cookiecutter.package_name }}.email.mail")
    def test_sends_message_within_app_context(
        self, mock_mail: MagicMock, app: Flask
    ) -> None:
        msg = MagicMock()
        send_async_email(app, msg)
        mock_mail.send.assert_called_once_with(msg)

    @patch("{{ cookiecutter.package_name }}.email.mail")
    def test_logs_error_on_smtp_failure(self, mock_mail: MagicMock, app: Flask) -> None:
        mock_mail.send.side_effect = OSError("SMTP connection refused")
        msg = MagicMock()
        msg.recipients = ["user@example.com"]
        msg.subject = "Confirm your email"

        with patch.object(app.logger, "exception") as mock_log:
            send_async_email(app, msg)

        mock_log.assert_called_once()
        log_message = mock_log.call_args[0][0]
        assert "Failed to send email" in log_message
