# {{ cookiecutter.friendly_name }}

[![PyPI](https://img.shields.io/pypi/v/{{ cookiecutter.project_name }})](https://img.shields.io/pypi/v/{{ cookiecutter.project_name }})
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/{{ cookiecutter.project_name }})](https://pypi.org/project/{{ cookiecutter.project_name }}/)
[![CI](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/actions/workflows/ci.yml)
[![Test](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/actions/workflows/test.yml/badge.svg)](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/actions/workflows/test.yml)
[![PyPI - License](https://img.shields.io/pypi/l/{{ cookiecutter.project_name }})](https://img.shields.io/pypi/l/{{ cookiecutter.project_name }})

{{ cookiecutter.short_description }}

## Installation

*{{ cookiecutter.friendly_name }}* is available on [PyPI](https://pypi.org/project/{{ cookiecutter.project_name }}/). Install with [uv](https://docs.astral.sh/uv/) or your package manager of choice:

```sh
uv add {{ cookiecutter.project_name }}
```

## Configuration

*{{ cookiecutter.friendly_name }}* is configured via environment variables. You can set them directly or prefix them with `FLASK_` to have Flask pick them up automatically (e.g. `FLASK_SECRET_KEY`).

| Variable                  | Description                                                                                                                                                            | Default                                |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| `SECRET_KEY`              | Secret key used for signing sessions, tokens, and cookies. Generate one with `python -c 'import secrets; print(secrets.token_urlsafe())'`. **Required in production.** | `please-change-this-to-something-else` |
| `SQLALCHEMY_DATABASE_URI` | Database connection URI.                                                                                                                                               | `sqlite:///default.sqlite`             |
| `MAIL_SERVER`             | SMTP server hostname.                                                                                                                                                  | `localhost`                            |
| `MAIL_PORT`               | SMTP server port.                                                                                                                                                      | `25`                                   |
| `MAIL_USE_TLS`            | Enable TLS.                                                                                                                                                            | `false`                                |
| `MAIL_USE_SSL`            | Enable SSL.                                                                                                                                                            | `false`                                |
| `MAIL_USERNAME`           | SMTP username.                                                                                                                                                         | `None`                                 |
| `MAIL_PASSWORD`           | SMTP password.                                                                                                                                                         | `None`                                 |
| `MAIL_DEFAULT_SENDER`     | Default sender address for outgoing emails.                                                                                                                            | `None`                                 |

## Usage

### Running the development server

Start the Flask development server with:

```sh
uv run flask run
```

The application will be available at <http://127.0.0.1:5000>.

### Running with Gunicorn

For production deployments, use [Gunicorn](https://gunicorn.org/):

```sh
gunicorn wsgi:app
```

### Features

The application provides the following features out of the box:

- **User registration** -- sign up with a username, email address, and password.
- **Email confirmation** -- new users receive a confirmation email with a tokenized link to verify their email address.
- **Login** -- authenticate with an email address and password, with an optional "remember me" feature.
- **Two-factor authentication (2FA)** -- optional TOTP-based two-factor authentication. Users can set up 2FA by scanning a QR code with an authenticator app.
- **Password reset** -- request a password reset email with a tokenized link to set a new password.
- **User listing** -- browse registered users and view individual user profiles.

### Routes

| Route                          | Description                         |
| ------------------------------ | ----------------------------------- |
| `/`                            | Index page.                         |
| `/users`                       | List all registered users.          |
| `/users/<name>`                | View user profile.                  |
| `/auth/register`               | Register a new account.             |
| `/auth/login`                  | Log in.                             |
| `/auth/logout`                 | Log out.                            |
| `/auth/confirmation/<token>`   | Confirm email address.              |
| `/auth/two-factor`             | Two-factor authentication prompt.   |
| `/auth/two-factor/setup`       | Set up two-factor authentication.   |
| `/auth/authenticate`           | Re-authenticate (password or TOTP). |
| `/auth/password-reset`         | Request a password reset.           |
| `/auth/password-reset/<token>` | Reset password.                     |

### Database migrations

Run database migrations with [Flask-Alembic](https://flask-alembic.readthedocs.io/):

```sh
uv run flask db upgrade
```
