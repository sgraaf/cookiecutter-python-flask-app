"""WSGI entry point for the Flask application.

Creates the application instance via the application factory function and
registers a shell context processor that exposes SQLAlchemy's orm module as
``so`` for convenience during interactive ``flask shell`` sessions.

Typical usage::

    flask run
    gunicorn wsgi:app
"""

import sqlalchemy.orm as so

from {{ cookiecutter.package_name }}.app import create_app

app = create_app()


@app.shell_context_processor
def make_shell_context() -> dict[str, object]:
    """Return objects to expose in the Flask shell context.

    Registered as a shell context processor so that the listed objects
    are automatically available when running ``flask shell``, without
    needing to import them manually.

    Returns:
        A dict mapping names to objects injected into the shell namespace.
    """
    return {"so": so}
