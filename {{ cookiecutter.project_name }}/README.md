# {{ cookiecutter.friendly_name }}

[![PyPI](https://img.shields.io/pypi/v/{{ cookiecutter.project_name }})](https://img.shields.io/pypi/v/{{ cookiecutter.project_name }})
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/{{ cookiecutter.project_name }})](https://pypi.org/project/{{ cookiecutter.project_name }}/)
[![CI](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/actions/workflows/ci.yml)
[![Test](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/actions/workflows/test.yml/badge.svg)](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/{{ cookiecutter.project_name }}/badge/?version=latest)](https://{{ cookiecutter.project_name }}.readthedocs.io/en/latest/?badge=latest)

{{ cookiecutter.short_description }}

## Installation

*{{ cookiecutter.friendly_name }}* is available on [PyPI](https://pypi.org/project/{{ cookiecutter.project_name }}/). Install with [uv](https://docs.astral.sh/uv/) or your package manager of choice:

```shell
uv add {{ cookiecutter.project_name }}
```

## Usage

### Add one

```python
from {{ cookiecutter.package_name }} import add_one


# add one to 3
four = add_one(3)
```
