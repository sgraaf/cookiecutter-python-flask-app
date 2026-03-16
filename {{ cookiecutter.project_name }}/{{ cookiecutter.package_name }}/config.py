"""Application configuration classes for {{ cookiecutter.friendly_name }}."""

import os
from typing import ClassVar

_DEFAULT_SECRET_KEY = "please-change-this-to-something-else"  # noqa: S105


class Config:
    """Base configuration shared across all environments."""

    # Flask builtin configuration values
    # https://flask.palletsprojects.com/en/stable/config/#builtin-configuration-values
    DEBUG: bool = False
    TESTING: bool = False
    # generate a nice key using `python -c 'import secrets; print(secrets.token_urlsafe())'`
    SECRET_KEY: str = os.environ.get("SECRET_KEY", _DEFAULT_SECRET_KEY)

    # SQLAlchemy engine configurations
    # https://flask-sqlalchemy-lite.readthedocs.io/en/stable/engine/#flask_sqlalchemy_lite.SQLALCHEMY_ENGINES
    SQLALCHEMY_ENGINES: ClassVar[dict[str, str]] = {
        "default": os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///default.sqlite")
    }

    # Mail configuration values
    # https://flask-mail.readthedocs.io/en/latest/#configuring
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", "25"))
    MAIL_USE_TLS: bool = os.environ.get("MAIL_USE_TLS", "").lower() in (
        "true",
        "on",
        "1",
    )
    MAIL_USE_SSL: bool = os.environ.get("MAIL_USE_SSL", "").lower() in (
        "true",
        "on",
        "1",
    )
    MAIL_USERNAME: str | None = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str | None = os.environ.get("MAIL_DEFAULT_SENDER")

    # Project configuration values
    PROJECT_TITLE: str = os.environ.get(
        "PROJECT_TITLE", "{{ cookiecutter.friendly_name }}"
    )
    PROJECT_SHORT_DESCRIPTION: str = os.environ.get(
        "PROJECT_SHORT_DESCRIPTION",
        "{{ cookiecutter.short_description }}",
    )
    PROJECT_AUTHOR: str = os.environ.get("PROJECT_AUTHOR", "{{ cookiecutter.author }}")
    PROJECT_EMAIL: str = os.environ.get("PROJECT_EMAIL", "{{ cookiecutter.email }}")
    PROJECT_COPYRIGHT_YEAR: str = os.environ.get("PROJECT_COPYRIGHT_YEAR", "{{ cookiecutter.copyright_year }}")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True


class TestingConfig(Config):
    """Testing configuration with an in-memory SQLite database."""

    TESTING: bool = True
    SQLALCHEMY_ENGINES: ClassVar[dict[str, str]] = {"default": "sqlite://"}


class ProductionConfig(Config):
    """Production configuration."""
