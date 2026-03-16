# cookiecutter-python-flask-app

[![Supported Python Versions](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://github.com/sgraaf/cookiecutter-python-flask-app)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![pyrefly](https://img.shields.io/endpoint?url=https://pyrefly.org/badge.json)](https://github.com/facebook/pyrefly)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![prek](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A [cookiecutter](https://cookiecutter.readthedocs.io/) template for creating a new Python web application with [Flask](https://flask.palletsprojects.com/).

See https://github.com/sgraaf/cookiecutter-python-flask-app-demo for a demo of this template.

## Usage

```shell
cookiecutter gh:sgraaf/cookiecutter-python-flask-app
```

## Features

- Lightweight WSGI web application with [Flask](https://flask.palletsprojects.com/), using the [application factory](https://flask.palletsprojects.com/en/stable/patterns/appfactories/) pattern
- Database ORM with [SQLAlchemy](https://www.sqlalchemy.org/) via [Flask-SQLAlchemy-Lite](https://flask-sqlalchemy-lite.readthedocs.io/)
- Database migrations with [Alembic](https://alembic.sqlalchemy.org/) via [Flask-Alembic](https://flask-alembic.readthedocs.io/)
- User authentication (registration, login, logout) with [Flask-Login](https://flask-login.readthedocs.io/)
- Form handling and validation with [WTForms](https://wtforms.readthedocs.io/) via [Flask-WTF](https://flask-wtf.readthedocs.io/)
- Email sending via [Flask-Mail](https://flask-mail.readthedocs.io/)
- Email confirmation and password reset using JSON Web Tokens (JWT) via [PyJWT](https://pyjwt.readthedocs.io/)
- Optional TOTP-based two-factor authentication via [PyOTP](https://pyauth.github.io/pyotp/)
- Semantic HTML styling via [Pico CSS](https://picocss.com/), including a light/dark theme toggle
- Linting with autofix (i.e. removing unused imports, detecting code smells and Python syntax upgrades) with [Ruff](https://docs.astral.sh/ruff/)
- Code formatting with [Ruff](https://docs.astral.sh/ruff/), [Mdformat](https://mdformat.readthedocs.io/en/stable/) and [Prettier](https://prettier.io/)
- Static type-checking with [mypy](http://www.mypy-lang.org/), [Pyrefly](https://pyrefly.org/) and [ty](https://docs.astral.sh/ty/)
- Checks and fixes before every commit with [prek](https://prek.j178.dev/)
- Testing with [pytest](https://docs.pytest.org/en/stable/)
- Extremely fast Python package and project management with [uv](https://docs.astral.sh/uv/)
- Continuous Integration with [GitHub Actions](https://github.com/features/actions)
- Automated version updates for GitHub Actions with [Dependabot](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot)

This template supports Python 3.11, 3.12, 3.13 and 3.14.
