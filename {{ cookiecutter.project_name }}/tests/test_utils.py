from __future__ import annotations

import datetime as dt
from base64 import b64decode
from typing import TYPE_CHECKING

import pytest

from {{ cookiecutter.package_name }}.utils import (
    camel_to_snake_case,
    generate_data_uri,
    generate_qrcode,
    pluralize,
    safe_redirect,
    slugify,
    utcnow,
)

if TYPE_CHECKING:
    from flask import Flask


@pytest.mark.unit
class TestCamelToSnakeCase:
    def test_simple(self) -> None:
        assert camel_to_snake_case("User") == "user"

    def test_two_words(self) -> None:
        assert camel_to_snake_case("UserProfile") == "user_profile"

    def test_multiple_words(self) -> None:
        assert camel_to_snake_case("MyLongClassName") == "my_long_class_name"

    def test_consecutive_uppercase(self) -> None:
        assert camel_to_snake_case("HTTPResponse") == "http_response"

    def test_single_char(self) -> None:
        assert camel_to_snake_case("A") == "a"

    def test_already_snake(self) -> None:
        assert camel_to_snake_case("user") == "user"

    def test_with_numbers(self) -> None:
        assert camel_to_snake_case("User2FA") == "user2_fa"

    def test_empty_string(self) -> None:
        """Test that an empty string returns an empty string."""
        assert camel_to_snake_case("") == ""

    def test_all_uppercase(self) -> None:
        """Test that an all-uppercase acronym is lowercased."""
        assert camel_to_snake_case("API") == "api"


@pytest.mark.unit
class TestPluralize:
    @pytest.mark.parametrize(
        ("noun", "expected"),
        [
            ("user", "users"),
            ("address", "addresses"),
            ("company", "companies"),
            ("status", "statuses"),
            ("category", "categories"),
            ("person", "people"),
            ("child", "children"),
            ("login_history", "login_histories"),
        ],
    )
    def test_pluralizes_correctly(self, noun: str, expected: str) -> None:
        """Test that pluralize() returns the correct English plural."""
        assert pluralize(noun) == expected

    def test_user_model_tablename(self) -> None:
        """Test that the concrete User model has the expected table name."""
        from {{ cookiecutter.package_name }}.models import User

        assert User.__tablename__ == "users"


@pytest.mark.unit
class TestUtcnow:
    def test_returns_utc_timezone(self) -> None:
        result = utcnow()
        assert result.tzinfo is dt.UTC

    def test_is_approximately_current_time(self) -> None:
        before = dt.datetime.now(dt.UTC)
        result = utcnow()
        after = dt.datetime.now(dt.UTC)
        assert before <= result <= after


@pytest.mark.unit
class TestSafeRedirect:
    """Tests for the safe_redirect helper."""

    def test_redirects_to_next_param(self, app: Flask) -> None:
        with app.test_request_context("/?next=/dashboard"):
            response = safe_redirect()
            assert response.status_code == 302
            assert response.location == "/dashboard"

    def test_falls_back_to_default_when_no_next(self, app: Flask) -> None:
        with app.test_request_context("/"):
            response = safe_redirect()
            assert response.status_code == 302
            # url_for("public.index") resolves to /
            assert "/" in response.location

    def test_rejects_external_url(self, app: Flask) -> None:
        with app.test_request_context("/?next=http://evil.com/steal"):
            response = safe_redirect()
            assert response.status_code == 302
            assert "evil.com" not in response.location

    def test_rejects_protocol_relative_url(self, app: Flask) -> None:
        with app.test_request_context("/?next=//evil.com/steal"):
            response = safe_redirect()
            assert response.status_code == 302
            assert "evil.com" not in response.location

    def test_custom_default(self, app: Flask) -> None:
        with app.test_request_context("/"):
            response = safe_redirect(default="auth.login")
            assert response.status_code == 302
            assert "/auth/login" in response.location

    def test_rejects_backslash_url(self, app: Flask) -> None:
        with app.test_request_context("/?next=\\evil.com"):
            response = safe_redirect()
            assert response.status_code == 302
            assert "evil.com" not in response.location

    def test_rejects_slash_backslash_url(self, app: Flask) -> None:
        with app.test_request_context("/?next=/\\evil.com"):
            response = safe_redirect()
            assert response.status_code == 302
            assert "evil.com" not in response.location

    def test_next_with_query_string(self, app: Flask) -> None:
        """Test that query parameters in the next URL are preserved."""
        with app.test_request_context("/?next=/dashboard%3Ftab%3Dsettings"):
            response = safe_redirect()
            assert response.status_code == 302
            assert response.location == "/dashboard?tab=settings"

    def test_next_with_fragment(self, app: Flask) -> None:
        """Test that fragment identifiers in the next URL are preserved."""
        with app.test_request_context("/?next=/page%23section"):
            response = safe_redirect()
            assert response.status_code == 302
            assert response.location == "/page#section"


@pytest.mark.unit
class TestSlugify:
    def test_basic_string(self) -> None:
        assert slugify("Hello World") == "hello-world"

    def test_numbers(self) -> None:
        assert slugify("Test 123") == "test-123"

    def test_special_characters_stripped(self) -> None:
        assert slugify("Hello World!") == "hello-world"

    def test_leading_trailing_hyphens_underscores_stripped(self) -> None:
        assert slugify("_hello-world_") == "hello-world"

    def test_multiple_spaces_hyphens_collapsed(self) -> None:
        assert slugify("hello   world") == "hello-world"

    def test_unicode_without_allow_unicode(self) -> None:
        assert slugify("Héllo Wörld") == "hello-world"

    def test_unicode_with_allow_unicode(self) -> None:
        assert slugify("Héllo Wörld", allow_unicode=True) == "héllo-wörld"

    def test_non_string_input_converted(self) -> None:
        assert slugify(42) == "42"

    def test_empty_string(self) -> None:
        assert slugify("") == ""

    def test_already_a_slug(self) -> None:
        assert slugify("hello-world") == "hello-world"

    def test_only_special_characters(self) -> None:
        """Test that a string of only special characters slugifies to empty."""
        assert slugify("!@#$%") == ""

    def test_whitespace_only(self) -> None:
        """Test that whitespace-only input slugifies to empty."""
        assert slugify("   ") == ""

    def test_unicode_emoji(self) -> None:
        """Test that emoji characters are stripped during slugification."""
        assert slugify("hello \U0001f30d world") == "hello-world"


@pytest.mark.unit
class TestGenerateQrcode:
    def test_returns_bytes(self) -> None:
        result = generate_qrcode("test")
        assert isinstance(result, bytes)

    def test_returns_non_empty_svg_content(self) -> None:
        result = generate_qrcode("test")
        assert len(result) > 0
        assert b"svg" in result.lower()

    def test_works_with_string_input(self) -> None:
        result = generate_qrcode("hello world")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_works_with_bytes_input(self) -> None:
        result = generate_qrcode(b"hello world")
        assert isinstance(result, bytes)
        assert len(result) > 0


@pytest.mark.unit
class TestGenerateDataUri:
    def test_string_data_without_media_type(self) -> None:
        assert generate_data_uri("hello") == "data:,hello"

    def test_string_data_with_media_type(self) -> None:
        assert (
            generate_data_uri("hello", media_type="text/plain")
            == "data:text/plain,hello"
        )

    def test_with_base64_encodes_data(self) -> None:
        result = generate_data_uri("hello", base64=True)
        assert result.startswith("data:;base64,")
        encoded_part = result.split(",", 1)[1]
        assert b64decode(encoded_part) == b"hello"

    def test_bytes_data_properly_decodes(self) -> None:
        result = generate_data_uri(b"hello")
        assert result == "data:,hello"

    def test_base64_with_bytes_input(self) -> None:
        result = generate_data_uri(b"hello", base64=True)
        assert ";base64," in result
        encoded_part = result.split(",", 1)[1]
        assert b64decode(encoded_part) == b"hello"

    def test_with_media_type_and_base64(self) -> None:
        result = generate_data_uri("hello", media_type="text/plain", base64=True)
        assert result.startswith("data:text/plain;base64,")
        encoded_part = result.split(",", 1)[1]
        assert b64decode(encoded_part) == b"hello"

    def test_empty_string_data(self) -> None:
        """Test that an empty string produces a minimal data URI."""
        assert generate_data_uri("") == "data:,"

    def test_empty_bytes_data(self) -> None:
        """Test that empty bytes produce a minimal data URI."""
        assert generate_data_uri(b"") == "data:,"
