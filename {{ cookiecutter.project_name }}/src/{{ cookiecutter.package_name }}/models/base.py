"""Base ORM model for {{ cookiecutter.friendly_name }}."""

import datetime as dt
import decimal
import uuid
from typing import Any

import sqlalchemy as sa
import sqlalchemy.orm as so

from {{ cookiecutter.package_name }}.utils import camel_to_snake_case, pluralize

from .mixins import CRUDMixin, QueryMixin


class Model(CRUDMixin, QueryMixin, so.DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    Inherits from so.DeclarativeBase to provide the declarative mapping
    interface. All application models should subclass this to share the same
    metadata and registry.
    """

    metadata = sa.MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
    type_annotation_map = {  # noqa: RUF012
        str: sa.Text,
        int: sa.Integer,
        float: sa.Numeric(asdecimal=False),
        bool: sa.Boolean,
        bytes: sa.LargeBinary,
        dt.date: sa.Date,
        dt.time: sa.Time,
        dt.datetime: sa.DateTime(timezone=True),
        uuid.UUID: sa.Uuid,
        decimal.Decimal: sa.Numeric(18, 6),
        dict[str, Any]: sa.JSON,
        list[Any]: sa.JSON,
    }

    __abstract__ = True

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    @so.declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return pluralize(camel_to_snake_case(cls.__name__))
