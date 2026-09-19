"""WSGI entry point for the Flask web application."""

import sqlalchemy as sa
import sqlalchemy.orm as so

from {{ cookiecutter.package_name }}.app import create_app
from {{ cookiecutter.package_name }}.extensions import db
from {{ cookiecutter.package_name }}.models import User

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
    return {"sa": sa, "so": so, "db": db, "User": User}
