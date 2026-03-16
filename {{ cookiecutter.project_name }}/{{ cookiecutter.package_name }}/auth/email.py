"""Email sending functions."""

from flask import render_template

from {{ cookiecutter.package_name }}.email import send_email
from {{ cookiecutter.package_name }}.models import User


def send_confirmation_email(user: User) -> None:
    """Send a confirmation email."""
    token = user.get_confirmation_token()
    send_email(
        subject="[{{ cookiecutter.friendly_name }}] Confirm your email address",
        recipients=[user.email_address],
        text_body=render_template(
            "auth/email/confirmation.txt", user=user, token=token
        ),
        html_body=render_template(
            "auth/email/confirmation.html", user=user, token=token
        ),
    )


def send_password_reset_email(user: User) -> None:
    """Send a password reset email."""
    token = user.get_password_reset_token()
    send_email(
        subject="[{{ cookiecutter.friendly_name }}] Reset your password",
        recipients=[user.email_address],
        text_body=render_template(
            "auth/email/reset_password.txt", user=user, token=token
        ),
        html_body=render_template(
            "auth/email/reset_password.html", user=user, token=token
        ),
    )
