"""Utility functions used throughout {{ cookiecutter.friendly_name }}."""

import datetime as dt
import io
import re
import unicodedata
from base64 import b64encode
from typing import Any
from urllib.parse import urlparse

import inflect
import qrcode
from flask import redirect, request, url_for
from qrcode.image.base import BaseImage
from qrcode.image.svg import SvgPathFillImage
from werkzeug import Response


def camel_to_snake_case(name: str) -> str:
    """Convert a ``CamelCase`` name to ``snake_case``."""
    name = re.sub(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))", r"_\1", name)
    return name.lower().lstrip("_")


def utcnow() -> dt.datetime:
    """Return the current UTC date and time."""
    return dt.datetime.now(dt.UTC)


def safe_redirect(default: str = "public.index") -> Response:
    r"""Redirect to the ``next`` query parameter, falling back to *default*.

    Rejects off-site URLs to prevent open-redirect attacks.  A valid *next*
    value must be a relative path starting with ``/`` and must not start with
    ``//`` or ``/\`` (which some browsers interpret as protocol-relative or
    host-relative URLs).
    """
    next_page = request.args.get("next")
    if (
        next_page is None
        or not next_page.startswith("/")
        or next_page.startswith(("//", "/\\"))
        or urlparse(next_page).netloc != ""
    ):
        next_page = url_for(default)
    return redirect(next_page)


def slugify(value: object, *, allow_unicode: bool = False) -> str:
    """Convert a value to a URL-friendly slug.

    Normalizes the input by removing or replacing characters that are not
    suitable for use in URLs. Optionally supports Unicode characters.

    Adapted from the Django:
    https://github.com/django/django/blob/476e5def5fcbcf637945985a23675db0e1f59354/django/utils/text.py#L466-L483

    Args:
        value: The value to slugify. Will be converted to a string.
        allow_unicode: If True, keeps Unicode characters using NFKC
            normalization. If False (default), converts to ASCII only by
            applying NFKD normalization and dropping non-ASCII characters.

    Returns:
        A lowercased slug with spaces and hyphens collapsed into single
        hyphens, and leading/trailing hyphens and underscores removed.
    """
    # convert the input to string
    value = str(value)

    if allow_unicode:
        # normalize unicode characters to their composed form (e.g. é stays é)
        value = unicodedata.normalize("NFKC", value)
    else:
        # decompose unicode characters (e.g. é -> e + combining accent),
        # then encode to ASCII and silently drop any non-ASCII bytes
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )

    # lowercase the string, then strip anything that isn't a word character,
    # whitespace, or hyphen (e.g. punctuation like commas, quotes, etc.)
    value = re.sub(r"[^\w\s-]", "", value.lower())

    # collapse consecutive hyphens and/or whitespace into a single hyphen,
    # then strip any leading or trailing hyphens and underscores
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def generate_qrcode(
    data: str | bytes,
    *,
    image_factory: type[BaseImage] = SvgPathFillImage,
    **kwargs: Any,  # noqa: ANN401
) -> bytes:
    """Generate a QR code for the given data."""
    with io.BytesIO() as buffer:
        qrcode.make(data, image_factory=image_factory, **kwargs).save(buffer)
        buffer.seek(0)
        return buffer.getvalue()


def generate_data_uri(
    data: str | bytes,
    *,
    media_type: str | None = None,
    base64: bool = False,
    encoding: str = "utf-8",
) -> str:
    """Generate a data URL for the given data."""
    if base64:
        data = b64encode(
            data.encode(encoding) if isinstance(data, str) else data
        ).decode("ascii")
    return f"data:{media_type if media_type is not None else ''}{';base64' if base64 else ''},{data.decode(encoding) if isinstance(data, bytes) else data}"


_inflect_engine = inflect.engine()


def pluralize(singular_noun: str) -> str:
    """Return the English plural form of *noun* on a best-effort basis (i.e., a noun that is already plural, might yield unexpected results)."""
    return _inflect_engine.plural_noun(singular_noun)
