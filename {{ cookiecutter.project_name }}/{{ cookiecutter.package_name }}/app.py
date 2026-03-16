"""App creation and configuration for {{ cookiecutter.friendly_name }}."""

import contextlib
import datetime as dt
from typing import Any

from flask import Flask, render_template
from flask_login import current_user
from werkzeug import Response

from .config import _DEFAULT_SECRET_KEY, Config, DevelopmentConfig
from .extensions import db
from .utils import utcnow


def configure_extensions(app: Flask) -> None:
    """Configure extensions."""
    from .extensions import alembic, login_manager, mail  # noqa: PLC0415
    from .models import Model, User  # noqa: PLC0415

    # Flask-SQLAlchemy-Lite
    db.init_app(app)

    # Flask-Alembic
    alembic.metadatas = {"default": Model.metadata}
    alembic.init_app(app)

    # Flask-Login
    login_manager.login_view = "auth.login"
    login_manager.refresh_view = "auth.authenticate"
    login_manager.login_message_category = "info"
    login_manager.needs_refresh_message_category = "info"

    @login_manager.user_loader
    def load_user(id_: int) -> User | None:
        """Loads the user. Required by the `login` extension."""
        return User.get_by(id=id_)

    login_manager.init_app(app)

    # Flask-Mail
    mail.init_app(app)


def configure_blueprints(app: Flask) -> None:
    """Configure blueprints."""
    from .auth import auth  # noqa: PLC0415
    from .public import public  # noqa: PLC0415

    app.register_blueprint(public)
    app.register_blueprint(auth)


def configure_context_processors(app: Flask) -> None:
    """Configure context processors."""

    @app.context_processor
    def inject_project_config() -> dict[str, dict[str, str]]:
        """Inject project configuration variables into the context of templates."""
        return {
            "project": {
                k.removeprefix("PROJECT_").lower(): v
                for k, v in app.config.items()
                if k.startswith("PROJECT_")
            }
        }


def configure_request_handlers(app: Flask) -> None:
    """Configure before/after request handlers."""

    @app.before_request
    def update_last_seen_at() -> None:
        """Update `last_seen_at` if the current user is authenticated.

        Uses ``commit=False`` so the write piggybacks on the request's own
        session flush instead of forcing a standalone COMMIT per request.
        An ``after_request`` hook commits any remaining dirty state.
        """
        if current_user.is_authenticated:
            current_user.update(last_seen_at=utcnow(), commit=False)

    @app.after_request
    def commit_session(response: Response) -> Response:
        """Commit the DB session after each request if it has pending changes.

        This ensures deferred writes (e.g. last_seen_at) are persisted
        without requiring every view to commit explicitly.
        """
        if db.session.new or db.session.dirty or db.session.deleted:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
        return response


def configure_error_handlers(app: Flask) -> None:
    """Register error handlers for common HTTP errors."""

    @app.errorhandler(401)
    def handle_401_unauthorized(error: Any) -> tuple[str, int]:  # noqa: ANN401, ARG001
        """Handle 401 Unauthorized errors."""
        return render_template("unauthorized.html"), 401

    @app.errorhandler(403)
    def handle_403_forbidden(error: Any) -> tuple[str, int]:  # noqa: ANN401, ARG001
        """Handle 403 Forbidden errors."""
        return render_template("forbidden.html"), 403

    @app.errorhandler(404)
    def handle_404_not_found(error: Any) -> tuple[str, int]:  # noqa: ANN401, ARG001
        """Handle 404 Not Found errors."""
        return render_template("not_found.html"), 404

    @app.errorhandler(500)
    def handle_500_internal_server_error(error: Any) -> tuple[str, int]:  # noqa: ANN401
        """Handle 500 Internal Server Error errors."""
        with contextlib.suppress(Exception):
            db.session.rollback()
        app.logger.error("Internal server error: %s", error)
        return render_template("internal_server_error.html"), 500

    @app.errorhandler(Exception)
    def handle_exception(error: Exception) -> tuple[str, int]:
        """Handle any unhandled exceptions."""
        with contextlib.suppress(Exception):
            db.session.rollback()
        app.logger.error("Unhandled exception: %s", error)
        return render_template("internal_server_error.html"), 500


def configure_template_filters(app: Flask) -> None:
    """Configure custom template filters."""
    from .utils import generate_data_uri, generate_qrcode  # noqa: PLC0415

    @app.template_filter("strftime")
    def strftime_filter(dt: dt.datetime, format_: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
        return dt.strftime(format_)

    @app.template_filter("qrcode_data_uri")
    def generate_qrcode_data_uri(data: str | bytes) -> str:
        return generate_data_uri(
            generate_qrcode(data), media_type="image/svg+xml", base64=True
        )


def create_app(config: type[Config] = DevelopmentConfig) -> Flask:
    """Create and configure a Flask application instance."""
    app = Flask(__name__)

    # configure app
    app.config.from_object(config)
    app.config.from_prefixed_env()

    # reject insecure `SECRET_KEY` in production
    if not app.debug and not app.testing:
        key = app.config.get("SECRET_KEY", "")
        if not key or key == _DEFAULT_SECRET_KEY:
            msg = "SECRET_KEY must be set to a secure value in production. Generate one with: `python -c 'import secrets; print(secrets.token_urlsafe())'`"
            raise ValueError(msg)

    # configure extensions
    configure_extensions(app)

    # configure blueprints
    configure_blueprints(app)

    # configure context processors
    configure_context_processors(app)

    # configure before request handlers
    configure_request_handlers(app)

    # configure error handlers
    configure_error_handlers(app)

    # configure template filters
    configure_template_filters(app)

    return app
