"""ORM model mixins for {{ cookiecutter.friendly_name }}."""

import datetime as dt
import math
from dataclasses import dataclass
from typing import Any, Generic, Self, TypeVar, cast

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import abort

from {{ cookiecutter.package_name }}.extensions import db
from {{ cookiecutter.package_name }}.utils import utcnow

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    """A page of query results with pagination metadata."""

    items: list[T]
    page: int
    per_page: int
    total: int

    @property
    def pages(self) -> int:
        """Total number of pages."""
        return math.ceil(self.total / self.per_page)

    @property
    def has_prev(self) -> bool:
        """Whether a previous page exists."""
        return self.page > 1

    @property
    def has_next(self) -> bool:
        """Whether a next page exists."""
        return self.page < self.pages


class CRUDMixin:
    """Mixin class with common CRUD operations for models."""

    @classmethod
    def create(cls, **kwargs: Any) -> Self:  # noqa: ANN401
        """Create a new instance and save it to the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, *, commit: bool = True, **kwargs: Any) -> Self:  # noqa: ANN401
        """Update the record given the keyword argument fields."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save(commit=commit)

    def save(self, *, commit: bool = True) -> Self:
        """Save the record to the database."""
        db.session.add(self)
        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
        return self

    def delete(self, *, commit: bool = True) -> None:
        """Remove the record from the database."""
        db.session.delete(self)
        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise


class QueryMixin:
    """Mixin class for querying models."""

    @classmethod
    def get(cls, *clauses: sa.ColumnExpressionArgument[bool]) -> Self | None:
        """Retrieve the first row matching the given WHERE clause(s)."""
        return db.session.scalar(sa.select(cls).where(*clauses))

    @classmethod
    def get_or_abort(cls, *clauses: sa.ColumnExpressionArgument[bool]) -> Self:
        """Retrieve the first row matching the given WHERE clause(s), or raise a 404 Not Found error."""
        result = cls.get(*clauses)
        if not result:
            abort(404)
        return result

    @classmethod
    def get_by(cls, **kwargs: Any) -> Self | None:  # noqa: ANN401
        """Retrieve the first row matching the given keyword argument filter(s)."""
        return db.session.scalar(sa.select(cls).filter_by(**kwargs))

    @classmethod
    def get_by_or_abort(cls, **kwargs: Any) -> Self:  # noqa: ANN401
        """Retrieve the first row matching the given keyword argument filter(s), or raise a 404 Not Found error."""
        result = cls.get_by(**kwargs)
        if not result:
            abort(404)
        return result

    @classmethod
    def get_all(cls, *clauses: sa.ColumnExpressionArgument[bool]) -> list[Self]:
        """Retrieve all rows matching the given WHERE clause(s)."""
        return list(db.session.scalars(sa.select(cls).where(*clauses)))

    @classmethod
    def count(
        cls,
        *clauses: sa.ColumnExpressionArgument[bool],
        column: so.InstrumentedAttribute[Any] | None = None,
    ) -> int:
        """Count rows in the table, optionally filtered by WHERE clauses."""
        if column is None:
            if hasattr(cls, "id"):
                column = cast("so.InstrumentedAttribute[int]", cls.id)
            else:
                msg = f"{cls.__name__} has no 'id' column. Provide an explicit 'column' argument to count()."
                raise ValueError(msg)

        return db.session.execute(
            sa.select(sa.func.count(column)).where(*clauses)
        ).scalar_one()

    @classmethod
    def paginate(
        cls,
        *clauses: sa.ColumnExpressionArgument[bool],
        page: int = 1,
        per_page: int = 20,
    ) -> Page[Self]:
        """Retrieve a paginated page of rows matching the given WHERE clause(s)."""
        if page < 1:
            msg = f"page must be >= 1, got {page}"
            raise ValueError(msg)
        if per_page < 1:
            msg = f"per_page must be >= 1, got {per_page}"
            raise ValueError(msg)

        total = cls.count(*clauses)
        items = list(
            db.session.scalars(
                sa.select(cls)
                .where(*clauses)
                .limit(per_page)
                .offset((page - 1) * per_page)
            )
        )
        return Page(items=items, page=page, per_page=per_page, total=total)


class TimestampMixin:
    """Mixin class for timestamping models."""

    created_at: so.Mapped[dt.datetime] = so.mapped_column(
        sa.DateTime(timezone=True), default=utcnow, server_default=sa.func.now()
    )
    updated_at: so.Mapped[dt.datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=sa.func.now(),
    )
