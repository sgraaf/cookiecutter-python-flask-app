"""Application configuration classes for {{ cookiecutter.friendly_name }}."""

import os
from typing import Any, ClassVar

from dotenv import load_dotenv

load_dotenv()

DEFAULT_SECRET_KEY = "please-change-this-to-something-else"  # noqa: S105


def env_bool(name: str, *, default: bool = False) -> bool:
    """Read a boolean from the environment.

    `1`, `true`, `yes` and `on` (case-insensitive) are true, anything else is false.
    An unset variable falls back to `default`.
    """
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Base configuration shared across all environments."""

    # Flask builtin configuration values
    # https://flask.palletsprojects.com/en/stable/config/#builtin-configuration-values
    DEBUG: bool = False
    TESTING: bool = False
    # generate a nice key using `python -c 'import secrets; print(secrets.token_urlsafe())'`
    SECRET_KEY: str = os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY)

    # SQLAlchemy engine configurations
    # https://flask-sqlalchemy-lite.readthedocs.io/en/stable/engine/#flask_sqlalchemy_lite.SQLALCHEMY_ENGINES
    SQLALCHEMY_ENGINES: ClassVar[dict[str, str]] = {
        "default": os.environ.get(
            "SQLALCHEMY_DATABASE_URI",
            "sqlite:///{{ cookiecutter.package_name }}.sqlite3",
        )
    }

    # Alembic configuration
    # https://flask-alembic.readthedocs.io/en/stable/config/
    ALEMBIC: ClassVar[dict[str, Any]] = {
        "file_template": "%%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s",
        "post_write_hooks": {
            "hooks": "prek",
            "prek.type": "exec",
            "prek.executable": "prek",
            "prek.options": "run --files REVISION_SCRIPT_FILENAME",
        },
    }

    # Mail configuration values
    # https://flask-mail.readthedocs.io/en/latest/#configuring
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", "25"))
    MAIL_USE_TLS: bool = env_bool("MAIL_USE_TLS")
    MAIL_USE_SSL: bool = env_bool("MAIL_USE_SSL")
    MAIL_USERNAME: str | None = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str | None = os.environ.get("MAIL_DEFAULT_SENDER")

    # App configuration values
    APP_TITLE: str = os.environ.get("APP_TITLE", "{{ cookiecutter.friendly_name }}")
    APP_SHORT_DESCRIPTION: str = os.environ.get(
        "APP_SHORT_DESCRIPTION",
        "{{ cookiecutter.short_description }}",
    )
    APP_AUTHOR: str = os.environ.get("APP_AUTHOR", "{{ cookiecutter.author }}")
    APP_EMAIL: str = os.environ.get("APP_EMAIL", "{{ cookiecutter.email }}")
    APP_COPYRIGHT_YEAR: str = os.environ.get("APP_COPYRIGHT_YEAR", "{{ cookiecutter.copyright_year }}")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True


class TestingConfig(Config):
    """Testing configuration with an in-memory SQLite database."""

    TESTING: bool = True
    SQLALCHEMY_ENGINES: ClassVar[dict[str, str]] = {"default": "sqlite:///:memory:"}


class ProductionConfig(Config):
    """Production configuration."""
