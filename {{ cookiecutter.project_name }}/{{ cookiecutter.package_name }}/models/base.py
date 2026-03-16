"""Base ORM model for {{ cookiecutter.friendly_name }}."""

import sqlalchemy.orm as so

from {{ cookiecutter.package_name }}.utils import camel_to_snake_case, pluralize

from .mixins import CRUDMixin, QueryMixin


class Model(CRUDMixin, QueryMixin, so.DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    Inherits from so.DeclarativeBase to provide the declarative mapping
    interface. All application models should subclass this to share the same
    metadata and registry.
    """

    __abstract__ = True

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    @so.declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:  # pyrefly: ignore[bad-override]
        return pluralize(camel_to_snake_case(cls.__name__))
