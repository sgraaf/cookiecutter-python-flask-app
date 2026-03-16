"""User ORM model for {{ cookiecutter.friendly_name }}."""

import datetime as dt
import time
from typing import Self

import jwt
import pyotp
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash

from {{ cookiecutter.package_name }}.utils import utcnow

from .base import Model
from .mixins import TimestampMixin


class User(TimestampMixin, UserMixin, Model):
    """ORM model representing a registered user."""

    email_address: so.Mapped[str] = so.mapped_column(
        sa.String(128), unique=True, index=True
    )
    username: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    otp_secret: so.Mapped[str] = so.mapped_column(
        sa.String(32), default=pyotp.random_base32
    )
    otp_enabled: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    last_totp_counter: so.Mapped[int | None] = so.mapped_column(sa.Integer)
    confirmed_at: so.Mapped[dt.datetime | None] = so.mapped_column(
        sa.DateTime(timezone=True)
    )
    last_seen_at: so.Mapped[dt.datetime | None] = so.mapped_column(
        sa.DateTime(timezone=True)
    )

    @hybrid_property  # pyrefly: ignore[bad-override]
    def is_active(self) -> bool:  # type: ignore[override]
        """A user is active iff their email address has been confirmed."""
        return self.confirmed_at is not None

    @is_active.inplace.expression
    @classmethod
    def _is_active_expression(cls) -> sa.ColumnElement[bool]:
        """SQL expression: confirmed_at IS NOT NULL."""
        return cls.confirmed_at.isnot(None)  # type: ignore[return-value]

    @so.validates("email_address")
    def _normalize_email(self, _key: str, value: str) -> str:
        """Lowercase email addresses on assignment for case-insensitive lookups."""
        return value.lower()

    @property
    def password(self) -> None:
        """Get the password.

        Raises:
            AttributeError: password is not a readable attribute.
        """
        msg = "password is not a readable attribute"
        raise AttributeError(msg)

    @password.setter
    def password(self, password: str) -> None:
        """Set the password."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """Check the password."""
        return check_password_hash(self.password_hash, password)

    @property
    def totp(self) -> pyotp.TOTP:
        """Get the time-based One Time Password (TOTP) handler."""
        return pyotp.TOTP(self.otp_secret)

    @property
    def otpauth_uri(self) -> str:
        """Get the TOTP provisioning URI."""
        return self.totp.provisioning_uri(
            name=self.email_address, issuer_name="{{ cookiecutter.friendly_name }}"
        )

    def verify_totp(self, totp: str) -> bool:
        """Verify the TOTP, rejecting replayed codes.

        Accepts codes within ±1 time step (``valid_window=1``) per RFC 6238.
        Each code can only be used once: once verified, the current time-step
        counter is stored and any code at or before that counter is rejected.
        """
        counter = int(time.time()) // self.totp.interval
        if self.last_totp_counter is not None and counter <= self.last_totp_counter:
            return False
        if not self.totp.verify(totp, valid_window=1):
            return False
        self.update(last_totp_counter=counter)
        return True

    def _encode_token(self, claim: str, expires_in: int = 3600) -> str:
        """Encode a JWT token with the given claim key and this user's ID."""
        return jwt.encode(
            payload={
                claim: self.id,
                "exp": utcnow() + dt.timedelta(seconds=expires_in),
            },
            key=current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @classmethod
    def _decode_token(cls, token: str, claim: str) -> Self | None:
        """Decode a JWT token and return the user identified by the given claim."""
        try:
            id_ = jwt.decode(
                jwt=token, key=current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )[claim]
        except (jwt.InvalidTokenError, KeyError):
            return None

        return cls.get_by(id=id_)

    def get_confirmation_token(self, expires_in: int = 3600) -> str:
        """Get a confirmation token."""
        return self._encode_token("confirmation", expires_in)

    @classmethod
    def verify_confirmation_token(cls, token: str) -> Self | None:
        """Verify the confirmation token."""
        return cls._decode_token(token, "confirmation")

    def get_password_reset_token(self, expires_in: int = 3600) -> str:
        """Get a password reset token."""
        return self._encode_token("password_reset", expires_in)

    @classmethod
    def verify_password_reset_token(cls, token: str) -> Self | None:
        """Verify the password reset token."""
        return cls._decode_token(token, "password_reset")
