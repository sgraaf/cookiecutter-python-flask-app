"""Authentication forms."""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    Field,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import Email, InputRequired, Length, Regexp, ValidationError

from {{ cookiecutter.package_name }}.models import User


class RegistrationForm(FlaskForm):
    """Registration form."""

    email_address = EmailField(
        "Email address", validators=[InputRequired(), Length(1, 128), Email()]
    )
    password = PasswordField("Password", validators=[InputRequired(), Length(8, 128)])
    username = StringField(
        "Username",
        validators=[
            InputRequired(),
            Length(1, 64),
            Regexp(
                r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,63}$",
                message="Username can only contain letters, numbers and dashes (-), and must start and end with either a letter or number.",
            ),
        ],
    )
    submit = SubmitField("Register")

    def validate_email_address(self, field: Field) -> None:
        """Validate the email address."""
        if User.get_by(email_address=field.data) is not None:
            msg = "There already exists an account using this email address."
            raise ValidationError(msg)

    def validate_username(self, field: Field) -> None:
        """Validate the username."""
        if User.get_by(username=field.data) is not None:
            msg = "There already exists an account this username."
            raise ValidationError(msg)


class LoginForm(FlaskForm):
    """Login form."""

    email_address = EmailField(
        "Email address", validators=[InputRequired(), Length(1, 128), Email()]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class PasswordAuthenticationForm(FlaskForm):
    """Password authentication form."""

    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Authenticate")


class TwoFactorAuthenticationForm(FlaskForm):
    """Two-factor authentication form."""

    token = StringField("Token", validators=[InputRequired(), Length(6, 6)])
    submit = SubmitField("Authenticate")


class PasswordResetRequestForm(FlaskForm):
    """Password reset request form."""

    email_address = EmailField("Email address", validators=[InputRequired(), Email()])
    submit = SubmitField("Request Password")


class PasswordResetForm(FlaskForm):
    """Password reset form."""

    password = PasswordField("Password", validators=[InputRequired(), Length(8, 128)])
    submit = SubmitField("Reset Password")
