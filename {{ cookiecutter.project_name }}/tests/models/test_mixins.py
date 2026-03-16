"""Tests for ORM model mixins."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

from {{ cookiecutter.package_name }}.models import User
from {{ cookiecutter.package_name }}.models.mixins import Page, QueryMixin

if TYPE_CHECKING:
    from typing import Any

    from flask import Flask
    from flask_sqlalchemy_lite import SQLAlchemy


@pytest.mark.unit
class TestPage:
    """Tests for Page dataclass."""

    def test_pages_rounds_up(self) -> None:
        page: Page[Any] = Page(items=[], page=1, per_page=10, total=25)
        assert page.pages == 3

    def test_pages_exact_division(self) -> None:
        page: Page[Any] = Page(items=[], page=1, per_page=10, total=20)
        assert page.pages == 2

    def test_pages_zero_total(self) -> None:
        page: Page[Any] = Page(items=[], page=1, per_page=10, total=0)
        assert page.pages == 0

    def test_has_prev_false_on_first_page(self) -> None:
        page: Page[Any] = Page(items=[], page=1, per_page=10, total=25)
        assert page.has_prev is False

    def test_has_prev_true_on_later_page(self) -> None:
        page: Page[Any] = Page(items=[], page=2, per_page=10, total=25)
        assert page.has_prev is True

    def test_has_next_true_when_more_pages(self) -> None:
        page: Page[Any] = Page(items=[], page=1, per_page=10, total=25)
        assert page.has_next is True

    def test_has_next_false_on_last_page(self) -> None:
        page: Page[Any] = Page(items=[], page=3, per_page=10, total=25)
        assert page.has_next is False

    def test_frozen(self) -> None:
        page: Page[Any] = Page(items=[], page=1, per_page=10, total=0)
        with pytest.raises(AttributeError):
            page.page = 2  # type: ignore[misc]


@pytest.mark.integration
class TestCRUDMixin:
    """Tests for CRUDMixin methods."""

    def test_create_persists_record(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="crud_create",
            email_address="crud_create@example.com",
            password="password123",
        )
        assert user.id is not None

    def test_update_changes_attributes(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="crud_update",
            email_address="crud_update@example.com",
            password="password123",
        )
        user.update(username="crud_updated")
        reloaded = User.get_by(id=user.id)
        assert reloaded is not None
        assert reloaded.username == "crud_updated"

    def test_update_without_commit(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="crud_nocommit",
            email_address="crud_nocommit@example.com",
            password="password123",
        )
        user.update(commit=False, username="changed_nocommit")
        assert user.username == "changed_nocommit"
        assert db.session.dirty or db.session.new

    def test_save_persists_changes(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="crud_save",
            email_address="crud_save@example.com",
            password="password123",
        )
        user.username = "crud_saved"
        user.save()
        reloaded = User.get_by(id=user.id)
        assert reloaded is not None
        assert reloaded.username == "crud_saved"

    def test_save_without_commit(self, app: Flask, db: SQLAlchemy) -> None:
        user = User(
            username="crud_save_nc",
            email_address="crud_save_nc@example.com",
            password_hash="dummy",
        )
        user.save(commit=False)
        assert user in db.session

    def test_delete_removes_record(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="crud_delete",
            email_address="crud_delete@example.com",
            password="password123",
        )
        user_id = user.id
        user.delete()
        assert User.get_by(id=user_id) is None

    def test_delete_without_commit(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="crud_del_nc",
            email_address="crud_del_nc@example.com",
            password="password123",
        )
        user.delete(commit=False)
        assert user in db.session.deleted


@pytest.mark.integration
class TestQueryMixin:
    """Tests for QueryMixin methods."""

    def test_get_returns_matching_record(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="query_get",
            email_address="query_get@example.com",
            password="password123",
        )
        result = User.get(User.id == user.id)
        assert result is not None
        assert result.id == user.id

    def test_get_returns_none_when_no_match(self, app: Flask, db: SQLAlchemy) -> None:
        result = User.get(User.id == -1)
        assert result is None

    def test_get_by_returns_matching_record(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="query_getby",
            email_address="query_getby@example.com",
            password="password123",
        )
        result = User.get_by(username="query_getby")
        assert result is not None
        assert result.id == user.id

    def test_get_by_returns_none_when_no_match(
        self, app: Flask, db: SQLAlchemy
    ) -> None:
        result = User.get_by(username="nonexistent_user_xyz")
        assert result is None

    def test_get_or_abort_returns_matching_record(
        self, app: Flask, db: SQLAlchemy
    ) -> None:
        user = User.create(
            username="query_abort",
            email_address="query_abort@example.com",
            password="password123",
        )
        result = User.get_or_abort(User.id == user.id)
        assert result.id == user.id

    def test_get_or_abort_raises_404(self, app: Flask, db: SQLAlchemy) -> None:
        with pytest.raises(Exception, match="404"):
            User.get_or_abort(User.id == -1)

    def test_get_by_or_abort_returns_matching_record(
        self, app: Flask, db: SQLAlchemy
    ) -> None:
        user = User.create(
            username="query_abort_by",
            email_address="query_abort_by@example.com",
            password="password123",
        )
        result = User.get_by_or_abort(username="query_abort_by")
        assert result.id == user.id

    def test_get_by_or_abort_raises_404(self, app: Flask, db: SQLAlchemy) -> None:
        with pytest.raises(Exception, match="404"):
            User.get_by_or_abort(username="nonexistent_user_xyz")

    def test_get_all_returns_all_records(self, app: Flask, db: SQLAlchemy) -> None:
        User.create(
            username="all_1",
            email_address="all_1@example.com",
            password="password123",
        )
        User.create(
            username="all_2",
            email_address="all_2@example.com",
            password="password123",
        )
        results = User.get_all()
        assert len(results) >= 2

    def test_get_all_returns_empty_list_when_no_records(
        self, app: Flask, db: SQLAlchemy
    ) -> None:
        results = User.get_all()
        assert results == []

    def test_get_all_with_filter_clause(self, app: Flask, db: SQLAlchemy) -> None:
        User.create(
            username="filtered_a",
            email_address="filtered_a@example.com",
            password="password123",
        )
        User.create(
            username="filtered_b",
            email_address="filtered_b@example.com",
            password="password123",
        )
        results = User.get_all(User.username == "filtered_a")
        assert len(results) == 1
        assert results[0].username == "filtered_a"

    def test_count_returns_total(self, app: Flask, db: SQLAlchemy) -> None:
        User.create(
            username="count_1",
            email_address="count_1@example.com",
            password="password123",
        )
        User.create(
            username="count_2",
            email_address="count_2@example.com",
            password="password123",
        )
        assert User.count() >= 2

    def test_count_with_filter_clause(self, app: Flask, db: SQLAlchemy) -> None:
        User.create(
            username="count_filter",
            email_address="count_filter@example.com",
            password="password123",
        )
        result = User.count(User.username == "count_filter")
        assert result == 1

    def test_count_with_multiple_clauses(self, app: Flask, db: SQLAlchemy) -> None:
        from {{ cookiecutter.package_name }}.utils import utcnow

        User.create(
            username="count_multi",
            email_address="count_multi@example.com",
            password="password123",
            confirmed_at=utcnow(),
        )
        result = User.count(User.username == "count_multi", User.is_active)
        assert result == 1

    def test_count_without_id_column_raises_value_error(
        self, app: Flask, db: SQLAlchemy
    ) -> None:
        """Test that count() raises ValueError when model has no 'id' column."""

        class NoIdModel(QueryMixin):
            pass

        with pytest.raises(ValueError, match="has no 'id' column"):
            NoIdModel.count()

    def test_paginate_first_page(self, app: Flask, db: SQLAlchemy) -> None:
        for i in range(5):
            User.create(
                username=f"pg_{i}",
                email_address=f"pg_{i}@example.com",
                password="password123",
            )
        result = User.paginate(page=1, per_page=2)
        assert len(result.items) == 2
        assert result.total == 5
        assert result.page == 1
        assert result.per_page == 2
        assert result.pages == 3
        assert result.has_prev is False
        assert result.has_next is True

    def test_paginate_last_page_partial(self, app: Flask, db: SQLAlchemy) -> None:
        for i in range(5):
            User.create(
                username=f"pglast_{i}",
                email_address=f"pglast_{i}@example.com",
                password="password123",
            )
        result = User.paginate(page=3, per_page=2)
        assert len(result.items) == 1
        assert result.has_prev is True
        assert result.has_next is False

    def test_paginate_beyond_last_page(self, app: Flask, db: SQLAlchemy) -> None:
        User.create(
            username="pgbeyond",
            email_address="pgbeyond@example.com",
            password="password123",
        )
        result = User.paginate(page=99, per_page=10)
        assert result.items == []
        assert result.total == 1

    def test_paginate_with_clauses(self, app: Flask, db: SQLAlchemy) -> None:
        from {{ cookiecutter.package_name }}.utils import utcnow

        User.create(
            username="pgfilter_a",
            email_address="pgfilter_a@example.com",
            password="password123",
            confirmed_at=utcnow(),
        )
        User.create(
            username="pgfilter_b",
            email_address="pgfilter_b@example.com",
            password="password123",
        )
        result = User.paginate(User.is_active, page=1, per_page=10)
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].username == "pgfilter_a"

    def test_paginate_empty_table(self, app: Flask, db: SQLAlchemy) -> None:
        result = User.paginate(page=1, per_page=10)
        assert result.items == []
        assert result.total == 0
        assert result.pages == 0
        assert result.has_prev is False
        assert result.has_next is False

    def test_paginate_invalid_page(self, app: Flask, db: SQLAlchemy) -> None:
        with pytest.raises(ValueError, match="page must be >= 1"):
            User.paginate(page=0)

    def test_paginate_invalid_per_page(self, app: Flask, db: SQLAlchemy) -> None:
        with pytest.raises(ValueError, match="per_page must be >= 1"):
            User.paginate(per_page=0)


@pytest.mark.integration
class TestTimestampMixin:
    """Tests for TimestampMixin columns."""

    def test_created_at_is_set_on_creation(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="ts_created",
            email_address="ts_created@example.com",
            password="password123",
        )
        assert user.created_at is not None

    def test_updated_at_is_set_on_creation(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="ts_updated",
            email_address="ts_updated@example.com",
            password="password123",
        )
        assert user.updated_at is not None

    def test_updated_at_changes_after_update(self, app: Flask, db: SQLAlchemy) -> None:
        user = User.create(
            username="ts_update_check",
            email_address="ts_update_check@example.com",
            password="password123",
        )
        original_updated_at = user.updated_at

        # Ensure wall-clock time advances so onupdate produces a distinct timestamp.
        time.sleep(0.01)

        user.update(username="ts_update_check_modified")
        assert user.updated_at > original_updated_at


@pytest.mark.integration
class TestCRUDMixinExceptionPaths:
    """Tests for CRUDMixin save/delete exception handling and rollback."""

    def test_save_rolls_back_on_commit_failure(
        self, app: Flask, db: SQLAlchemy
    ) -> None:
        """Test that save() rolls back the session when commit raises."""
        from unittest.mock import patch

        import sqlalchemy.exc

        user = User.create(
            username="exc_save",
            email_address="exc_save@example.com",
            password="password123",
        )
        user.username = "exc_save_changed"
        with (
            patch.object(
                db.session,
                "commit",
                side_effect=sqlalchemy.exc.IntegrityError("test", {}, Exception()),
            ),
            pytest.raises(sqlalchemy.exc.IntegrityError),
        ):
            user.save()

    def test_delete_rolls_back_on_commit_failure(
        self, app: Flask, db: SQLAlchemy
    ) -> None:
        """Test that delete() rolls back the session when commit raises."""
        from unittest.mock import patch

        import sqlalchemy.exc

        user = User.create(
            username="exc_delete",
            email_address="exc_delete@example.com",
            password="password123",
        )
        with (
            patch.object(
                db.session,
                "commit",
                side_effect=sqlalchemy.exc.IntegrityError("test", {}, Exception()),
            ),
            pytest.raises(sqlalchemy.exc.IntegrityError),
        ):
            user.delete()
