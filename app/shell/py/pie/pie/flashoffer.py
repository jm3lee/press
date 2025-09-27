"""Render landing page call-to-action buttons.

This module provides helpers equivalent to the ``primary_cta`` and
``outline_cta`` Jinja macros that live alongside landing page templates.
The functions return ``Markup`` strings so they can be used directly from
Jinja without additional escaping. Attribute handling mirrors the macros:
optional ``rel``/``target`` parameters are appended only when supplied and
any extra keyword arguments are rendered verbatim as HTML attributes.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from markupsafe import Markup, escape

__all__ = ["primary_cta", "outline_cta"]


def _merge_attrs(
    base_classes: str,
    href: str,
    extra_classes: str,
    rel: str | None,
    target: str | None,
    attrs: dict[str, Any],
) -> Iterable[tuple[str, Markup]]:
    """Yield escaped attribute/value pairs for rendering."""

    class_list = base_classes
    if extra_classes:
        class_list = f"{class_list} {extra_classes}"

    pairs: list[tuple[str, Any]] = [
        ("class", class_list),
        ("href", href),
    ]
    if rel is not None:
        pairs.append(("rel", rel))
    if target is not None:
        pairs.append(("target", target))
    pairs.extend(attrs.items())

    for name, value in pairs:
        if value is None:
            continue
        yield (escape(str(name)), escape(str(value)))


def _render_cta(
    base_classes: str,
    text: str | Markup,
    href: str,
    *,
    extra_classes: str = "",
    rel: str | None = None,
    target: str | None = None,
    **attrs: Any,
) -> Markup:
    """Return a button-style anchor tag matching the landing CTA macros."""

    attr_html = " ".join(
        f"{name}=\"{value}\"" for name, value in _merge_attrs(
            base_classes,
            href,
            extra_classes,
            rel,
            target,
            attrs,
        )
    )
    if isinstance(text, Markup):
        label = text
    else:
        label = escape(text)
    return Markup(f"<a {attr_html}>{label}</a>")


def primary_cta(
    text: str | Markup,
    href: str,
    extra_classes: str = "",
    rel: str | None = None,
    target: str | None = None,
    **attrs: Any,
) -> Markup:
    """Render the primary call-to-action button."""

    return _render_cta(
        "btn btn-primary btn-lg px-4",
        text,
        href,
        extra_classes=extra_classes,
        rel=rel,
        target=target,
        **attrs,
    )


def outline_cta(
    text: str | Markup,
    href: str,
    extra_classes: str = "",
    rel: str | None = None,
    target: str | None = None,
    **attrs: Any,
) -> Markup:
    """Render the outline-style call-to-action button."""

    return _render_cta(
        "btn btn-outline-light btn-lg px-4",
        text,
        href,
        extra_classes=extra_classes,
        rel=rel,
        target=target,
        **attrs,
    )
