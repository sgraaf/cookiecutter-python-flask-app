"""Email sending utilities for {{ cookiecutter.friendly_name }}."""

from threading import Thread
from typing import Any

from flask import current_app
from flask.app import Flask
from flask_mail import Message

from .extensions import mail


def send_async_email(app: Flask, msg: Message) -> None:
    """Send an email message within a Flask application context."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception:
            app.logger.exception(
                "Failed to send email to %s with subject '%s'",
                msg.recipients,
                msg.subject,
            )


def send_email(
    subject: str,
    recipients: list[str | tuple[str, str]],
    text_body: str,
    html_body: str,
    **kwargs: Any,  # noqa: ANN401
) -> None:
    """Compose and send an email asynchronously in a background thread."""
    Thread(
        target=send_async_email,
        args=(
            current_app._get_current_object(),  # type: ignore[attr-defined]
            Message(
                subject, recipients=recipients, body=text_body, html=html_body, **kwargs
            ),
        ),
    ).start()
