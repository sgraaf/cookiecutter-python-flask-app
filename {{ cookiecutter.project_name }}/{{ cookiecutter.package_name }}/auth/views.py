"""Views of the auth module."""

from typing import cast

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    confirm_login,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug import Response

from {{ cookiecutter.package_name }}.models import User
from {{ cookiecutter.package_name }}.utils import safe_redirect, utcnow

from . import auth
from .email import send_confirmation_email, send_password_reset_email
from .forms import (
    LoginForm,
    PasswordAuthenticationForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    RegistrationForm,
    TwoFactorAuthenticationForm,
)

# happy path
# 1. register
# 2. confirm email address
# 3. login
# 4. 2fa (optional)
# 5. logout

# additional
# a. 2fa set-up
# b. reset password

# to do
# a. change password
# b. change email address


@auth.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    """Registration."""
    # user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # create user
        user = User.create(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password.data,
        )

        # send confirmation email
        send_confirmation_email(user)

        # redirect to login page
        flash(
            "Thank you for signing up! A confirmation email has been sent to your email address.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth.route("/confirmation/<token>")
def confirmation(token: str) -> Response:
    """Confirmation."""
    # user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    user = User.verify_confirmation_token(token)

    # couldn't verify token
    if user is None:
        flash("The confirmation link is invalid or has expired.")
        return redirect(url_for("public.index"))

    # mark user as confirmed
    user.update(confirmed_at=utcnow())
    flash("Your email address is confirmed.", "success")

    # redirect to login page
    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    """Login."""
    # user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = LoginForm()
    if form.validate_on_submit():
        # get user by their email address
        user = User.get_by(email_address=cast("str", form.email_address.data).lower())

        # verify password (first factor)
        if user is None or not user.verify_password(cast("str", form.password.data)):
            flash("Invalid email address or password.", "danger")
            return redirect(url_for("auth.login"))

        # verify user is active
        if not user.is_active:
            flash(
                "First confirm your email address before you try to login.",
                "danger",
            )
            return redirect(url_for("auth.login"))

        remember_me = form.remember_me.data

        # possibly verify TOTP token (second factor)
        if user.otp_enabled:
            # store the user's id and "remember me" in the session
            session["user_id"] = user.id
            session["remember_me"] = remember_me
            return redirect(url_for("auth.two_factor", next=request.args.get("next")))

        # all checks passed, clear the session and log user in
        session.clear()
        login_user(user, remember=remember_me)

        # redirect to the next page
        return safe_redirect()

    return render_template("auth/login.html", form=form)


@auth.route("/two-factor", methods=["GET", "POST"])
def two_factor() -> str | Response:
    """Two-factor authentication."""
    # user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    # user_id is not in session
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.get_by(id=session.get("user_id"))

    # this shouldn't happen
    if user is None:
        session.pop("user_id", None)
        flash("Something went wrong during two-factor authentication.", "danger")
        return redirect(url_for("auth.login"))

    form = TwoFactorAuthenticationForm()
    if form.validate_on_submit():
        # verify TOTP token
        if not user.verify_totp(cast("str", form.token.data)):
            flash("Invalid token", "danger")
            return render_template("auth/two-factor.html", form=form)

        # all checks passed, clear the session and log user in
        remember_me = session.pop("remember_me", False)
        session.clear()
        login_user(user, remember=remember_me)

        # redirect to the next page
        return safe_redirect()

    return render_template("auth/two-factor.html", form=form)


@auth.route("/authenticate", methods=["GET", "POST"])
@login_required
def authenticate() -> str | Response:
    """Authenticate."""
    is_totp = current_user.otp_enabled
    if is_totp:
        form = TwoFactorAuthenticationForm()
        if form.validate_on_submit():
            # verify TOTP token
            if current_user.verify_totp(cast("str", form.token.data)):
                confirm_login()

                # redirect to the next page
                return safe_redirect()

            flash("Invalid token", "danger")
    else:
        form = PasswordAuthenticationForm()
        if form.validate_on_submit():
            # verify password
            if current_user.verify_password(cast("str", form.password.data)):
                confirm_login()

                # redirect to the next page
                return safe_redirect()

            flash("Invalid password", "danger")

    return render_template("auth/authenticate.html", form=form, is_totp=is_totp)


@auth.route("/logout")
def logout() -> Response:
    """Logout."""
    logout_user()
    return redirect(url_for("public.index"))


@auth.route("/two-factor/setup", methods=["GET", "POST"])
@login_required
def two_factor_setup() -> tuple[str, int, dict[str, str]] | Response:
    """Two-factor set-up."""
    form = TwoFactorAuthenticationForm()

    if request.method == "GET":
        session["data"] = current_user.otpauth_uri

    if form.validate_on_submit():
        # verify TOTP token
        if not current_user.verify_totp(form.token.data):
            flash("Invalid token, please try again.", "danger")
            return redirect(url_for("auth.two_factor_setup"))

        # enable OTP
        current_user.update(otp_enabled=True)
        flash("Two-factor authentication has been set-up successfully.", "success")
        return redirect(url_for("public.index"))

    return (
        render_template("auth/two-factor-setup.html", user=current_user, form=form),
        200,
        {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@auth.route("/password-reset", methods=["GET", "POST"])
def password_reset_request() -> str | Response:
    """Password reset request."""
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        if (
            user := User.get_by(
                email_address=cast("str", form.email_address.data).lower()
            )
        ) is not None:
            send_password_reset_email(user)
        flash(
            "Check your inbox for instructions to reset your password.",
            "warning",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/password-reset-request.html", form=form)


@auth.route("/password-reset/<string:token>", methods=["GET", "POST"])
def password_reset_confirmation(token: str) -> str | Response:
    """Password reset."""
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    if (user := User.verify_password_reset_token(token)) is None:
        return redirect(url_for("public.index"))

    form = PasswordResetForm()
    if form.validate_on_submit():
        user.update(password=form.password.data)
        flash("Your password has been reset.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/password-reset.html", form=form)
