"""Render landing page call-to-action buttons.

This module provides helpers equivalent to the ``primary_cta`` and
``outline_cta`` Jinja macros that live alongside landing page templates.
The functions return ``Markup`` strings so they can be used directly from
Jinja without additional escaping. Attribute handling mirrors the macros:
optional ``rel``/``target`` parameters are appended only when supplied and
any extra keyword arguments are rendered verbatim as HTML attributes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from markupsafe import Markup, escape

__all__ = ["primary_cta", "outline_cta", "preview_card", "footer"]


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


def _require_card_value(card: Mapping[str, Any], key: str) -> Any:
    try:
        return card[key]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise KeyError(
            "preview_card() card mapping is missing required key " f"'{key}'"
        ) from exc


def _escape_attr_value(value: Any) -> Markup:
    return escape(str(value))


def _coerce_html(value: Any) -> Markup:
    if isinstance(value, Markup):
        return value
    return escape(value)


def preview_card(card: Mapping[str, Any]) -> Markup:
    """Render the Flashoffer preview card partial."""

    image_url = _escape_attr_value(_require_card_value(card, "image_url"))
    alt_text = _escape_attr_value(_require_card_value(card, "alt_text"))
    link_href = _escape_attr_value(_require_card_value(card, "link_href"))
    caption = _coerce_html(_require_card_value(card, "caption"))

    return Markup(
        (
            '<div class="col">\n'
            '  <div class="card h-100 bg-dark border border-light-subtle shadow-sm">\n'
            '    <div\n'
            '      class="card-img-top bg-black d-flex align-items-center justify-content-center rounded-top overflow-hidden position-relative preview-card"\n'
            '    >\n'
            '      <img\n'
            f'        src="{image_url}"\n'
            '        class="img-fluid w-100 h-auto preview-image"\n'
            f'        alt="{alt_text}"\n'
            '        loading="lazy"\n'
            '      />\n'
            '      <div class="preview-overlay">\n'
            '        <div class="text-center px-3">\n'
            '          <p class="mb-2 fw-semibold">Tap to reveal this artistic nude pose.</p>\n'
            f'          <a class="btn btn-outline-light btn-sm preview-toggle" href="{link_href}" role="button">\n'
            '            View image\n'
            '          </a>\n'
            '        </div>\n'
            '      </div>\n'
            '    </div>\n'
            '    <div class="card-body">\n'
            f'      <p class="card-text mb-0 text-white-50">{caption}</p>\n'
            '    </div>\n'
            '  </div>\n'
            '</div>'
        )
    )


def _coerce_optional_html(value: str | Markup | None) -> Markup:
    if value is None:
        return Markup("")
    return _coerce_html(value)


def footer(
    *,
    container_id: str = "contact",
    left_prefix: str | Markup | None = Markup("©&nbsp;"),
    site_name: str | Markup = "Seattle Figure Studio",
    site_href: str = "https://seattlefigurestudio.com",
    rights_statement: str | Markup = "All rights reserved.",
    email_label: str | Markup = "brian@seattlefigurestudio.com",
    email_href: str = "mailto:brian@seattlefigurestudio.com",
) -> Markup:
    """Render the Flashoffer footer snippet."""

    id_attr = _escape_attr_value(container_id)
    site_href_attr = _escape_attr_value(site_href)
    email_href_attr = _escape_attr_value(email_href)

    prefix_html = _coerce_optional_html(left_prefix)
    site_html = _coerce_html(site_name)
    rights_html = _coerce_html(rights_statement)
    email_html = _coerce_html(email_label)

    return Markup(
        (
            f'<footer id="{id_attr}" class="container py-4 small">\n'
            '  <div class="row gy-3 align-items-center">\n'
            '    <div class="col-12 col-md">\n'
            f'      {prefix_html}<a\n'
            '        class="link-dark text-decoration-none"\n'
            f'        href="{site_href_attr}"\n'
            '      >\n'
            f'        {site_html}\n'
            f'      </a>. {rights_html}\n'
            '    </div>\n'
            '    <div class="col-12 col-md-auto">\n'
            f'      <a class="fw-semibold" href="{email_href_attr}">\n'
            f'        {email_html}\n'
            '      </a>\n'
            '    </div>\n'
            '  </div>\n'
            '</footer>'
        )
    )
