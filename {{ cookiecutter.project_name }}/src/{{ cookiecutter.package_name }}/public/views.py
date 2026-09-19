"""Views of the public module."""

from typing import cast

from flask import current_app, render_template, request, send_from_directory
from werkzeug import Response

from {{ cookiecutter.package_name }}.models import User

from . import public


@public.route("/")
@public.route("/index")
def index() -> str:
    """Index page."""
    return render_template("index.html")


@public.route("/users")
def users() -> str:
    """Users page."""
    users: list[User] = User.get_all()
    return render_template("users.html", users=users)


@public.route("/users/<string:name>")
def user(name: str) -> str:
    """Users page."""
    user: User = User.get_or_abort(User.username == name)
    return render_template("user.html", user=user)


@public.route("/favicon.svg")
@public.route("/favicon.png")
@public.route("/robots.txt")
def static_from_root() -> Response:
    """Static files served from the site's root."""
    return send_from_directory(cast("str", current_app.static_folder), request.path[1:])
