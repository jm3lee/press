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

from dominate import tags
from dominate.util import raw
from markupsafe import Markup, escape

__all__ = [
    "primary_cta",
    "outline_cta",
    "hero_banner",
    "section_header",
    "preview_card",
    "footer",
]


def _merge_attrs(
    base_classes: str,
    href: str,
    extra_classes: str,
    rel: str | None,
    target: str | None,
    attrs: dict[str, Any],
) -> Iterable[tuple[str, str]]:
    """Yield attribute/value pairs for rendering."""

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
        yield (str(name), str(value))


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

    link = tags.a()
    for name, value in _merge_attrs(
        base_classes,
        href,
        extra_classes,
        rel,
        target,
        attrs,
    ):
        if name == "class":
            link["class"] = value
        else:
            link[name] = value

    label = _coerce_html(text)
    link.add(raw(str(label)))
    return Markup(link.render())


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


def _coerce_mapping(mapping: Mapping[str, Any] | None) -> dict[str, Any]:
    if mapping is None:
        return {}
    return dict(mapping)


def hero_banner(
    *,
    eyebrow: str | Markup = "Seattle-born figure reference",
    title: str | Markup = "Stone Canvas",
    description: str | Markup = (
        "Build stronger drawings with Stone Canvas reference bundles created by "
        "Seattle models and artists. Each pack keeps studies aligned with atelier "
        "methods, community collaborations, and clear licensing."
    ),
    primary_cta_text: str | Markup = "Explore Stone Canvas",
    primary_cta_href: str = "https://seattlefigurestudio.com/shop/stone-canvas-medusa",
    primary_cta_kwargs: Mapping[str, Any] | None = None,
    first_outline_text: str | Markup = "Email to collaborate",
    first_outline_href: str = "mailto:brian@seattlefigurestudio.com",
    first_outline_kwargs: Mapping[str, Any] | None = None,
    second_outline_text: str | Markup = "Meet Seattle Figure Studio",
    second_outline_href: str = "https://seattlefigurestudio.com/about-us",
    second_outline_kwargs: Mapping[str, Any] | None = None,
    hero_image_url: str | None = None,
    hero_image_alt: str | Markup | None = None,
    hero_image_kwargs: Mapping[str, Any] | None = None,
) -> Markup:
    """Render the Flashoffer hero banner with configurable CTAs."""

    eyebrow_html = _coerce_html(eyebrow)
    title_html = _coerce_html(title)
    description_html = _coerce_html(description)

    primary_kwargs = _coerce_mapping(primary_cta_kwargs)
    first_outline = _coerce_mapping(first_outline_kwargs)
    second_outline = _coerce_mapping(second_outline_kwargs)

    primary_button = primary_cta(primary_cta_text, primary_cta_href, **primary_kwargs)
    first_outline_button = outline_cta(
        first_outline_text,
        first_outline_href,
        **first_outline,
    )
    second_outline_button = outline_cta(
        second_outline_text,
        second_outline_href,
        **second_outline,
    )

    hero_background_style = (
        "background: var("
        "--flashoffer-hero-background, "
        "radial-gradient(circle at 10% -10%, "
        "rgba(255, 92, 92, 0.18), transparent 45%), "
        "radial-gradient(circle at 110% 20%, "
        "rgba(34, 139, 230, 0.16), transparent 55%), "
        "var(--press-background, #090b10)"
        ");"
    )

    section_tag = tags.section(_class="section")
    container = section_tag.add(tags.div(_class="container"))
    row = container.add(tags.div(_class="row justify-content-center"))
    column = row.add(tags.div(_class="col-lg-10"))
    surface = column.add(
        tags.div(
            _class="surface p-4 p-md-5 text-center",
            style=hero_background_style,
        )
    )

    eyebrow_span = surface.add(tags.span(_class="eyebrow mb-3 d-inline-block"))
    eyebrow_span.add(raw(str(eyebrow_html)))

    title_heading = surface.add(tags.h1(_class="display-5 fw-semibold mb-3"))
    title_heading.add(raw(str(title_html)))

    description_paragraph = surface.add(
        tags.p(
            _class="lead mx-auto mb-4",
            style="max-width: 38rem;",
        )
    )
    description_paragraph.add(raw(str(description_html)))

    if hero_image_url is not None:
        image_wrapper = surface.add(
            tags.div(_class="hero-visual-wrapper mx-auto mb-4")
        )
        image_attrs = _coerce_mapping(hero_image_kwargs)
        image_classes = "hero-visual img-fluid"
        extra_classes = image_attrs.pop("class", "")
        if extra_classes:
            image_classes = f"{image_classes} {extra_classes}"
        extra_classes = image_attrs.pop("extra_classes", "")
        if extra_classes:
            image_classes = f"{image_classes} {extra_classes}"

        hero_image_alt_value = "" if hero_image_alt is None else hero_image_alt

        sanitized_attrs: dict[str, str] = {
            "src": _escape_attr_value(hero_image_url),
            "alt": _escape_attr_value(hero_image_alt_value),
        }

        loading_value = image_attrs.pop("loading", "lazy")
        if loading_value is not None:
            sanitized_attrs["loading"] = _escape_attr_value(loading_value)

        for name, value in image_attrs.items():
            if value is None:
                continue
            sanitized_attrs[name] = _escape_attr_value(value)

        image_wrapper.add(
            tags.img(
                _class=image_classes,
                **sanitized_attrs,
            )
        )

    cta_container = surface.add(
        tags.div(_class="hero-cta d-grid gap-3 d-sm-flex justify-content-center")
    )
    cta_container.add(raw(str(primary_button)))
    cta_container.add(raw(str(first_outline_button)))
    cta_container.add(raw(str(second_outline_button)))

    return Markup(section_tag.render())


def _require_card_value(card: Mapping[str, Any], key: str) -> Any:
    try:
        return card[key]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise KeyError(
            "preview_card() card mapping is missing required key " f"'{key}'"
        ) from exc


def _escape_attr_value(value: Any) -> str:
    return str(value)


def _coerce_html(value: Any) -> Markup:
    if isinstance(value, Markup):
        return value
    return escape(value)


def preview_card(
    card: Mapping[str, Any],
    *,
    overlay_text: str | Markup = "Tap to reveal this artistic nude pose.",
    overlay_button_text: str | Markup = "View image",
) -> Markup:
    """Render the Flashoffer preview card partial."""

    image_url = _escape_attr_value(_require_card_value(card, "image_url"))
    alt_text = _escape_attr_value(_require_card_value(card, "alt_text"))
    link_href = _escape_attr_value(_require_card_value(card, "link_href"))
    caption = _coerce_html(_require_card_value(card, "caption"))
    overlay_html = _coerce_html(overlay_text)
    overlay_button_html = _coerce_html(overlay_button_text)

    card_column = tags.div(_class="col")
    card_root = card_column.add(
        tags.div(_class="card h-100 bg-dark border border-light-subtle shadow-sm")
    )
    image_wrapper = card_root.add(
        tags.div(
            _class=(
                "card-img-top bg-black d-flex align-items-center "
                "justify-content-center rounded-top overflow-hidden "
                "position-relative preview-card"
            )
        )
    )
    image_wrapper.add(
        tags.img(
            src=image_url,
            _class="img-fluid w-100 h-auto preview-image",
            alt=alt_text,
            loading="lazy",
        )
    )
    overlay = image_wrapper.add(tags.div(_class="preview-overlay"))
    overlay_inner = overlay.add(tags.div(_class="text-center px-3"))
    overlay_text_paragraph = overlay_inner.add(tags.p(_class="mb-2 fw-semibold"))
    overlay_text_paragraph.add(raw(str(overlay_html)))
    overlay_button = overlay_inner.add(
        tags.a(
            _class="btn btn-outline-light btn-sm preview-toggle",
            href=link_href,
            role="button",
        )
    )
    overlay_button.add(raw(str(overlay_button_html)))
    card_body = card_root.add(tags.div(_class="card-body"))
    caption_paragraph = card_body.add(
        tags.p(_class="card-text mb-0 text-white-50")
    )
    caption_paragraph.add(raw(str(caption)))

    return Markup(card_column.render())


def _coerce_optional_html(value: str | Markup | None) -> Markup:
    if value is None:
        return Markup("")
    return _coerce_html(value)


def section_header(
    *,
    eyebrow: str | Markup | None = None,
    title: str | Markup | None = None,
    body_html: str | Markup | None = None,
) -> Markup:
    """Render a centered section header."""

    row = tags.div(_class="row justify-content-center mb-5 text-center")
    column = row.add(tags.div(_class="col-lg-8"))

    if eyebrow is not None:
        eyebrow_html = _coerce_html(eyebrow)
        eyebrow_span = column.add(
            tags.span(_class="eyebrow mb-3 d-inline-block text-white-50")
        )
        eyebrow_span.add(raw(str(eyebrow_html)))

    if title is not None:
        title_html = _coerce_html(title)
        title_heading = column.add(tags.h2(_class="fw-semibold mb-3"))
        title_heading.add(raw(str(title_html)))

    if body_html is not None:
        body_markup = _coerce_html(body_html)
        body_paragraph = column.add(tags.p(_class="mb-0 text-white-50"))
        body_paragraph.add(raw(str(body_markup)))

    return Markup(row.render())


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

    prefix_html = _coerce_optional_html(left_prefix)
    site_html = _coerce_html(site_name)
    rights_html = _coerce_html(rights_statement)
    email_html = _coerce_html(email_label)

    footer_tag = tags.footer(
        id=str(container_id),
        _class="container py-4 small",
    )
    row = footer_tag.add(tags.div(_class="row gy-3 align-items-center"))

    left_column = row.add(tags.div(_class="col-12 col-md"))
    if prefix_html:
        left_column.add(raw(str(prefix_html)))
    site_link = left_column.add(
        tags.a(
            _class="link text-decoration-none",
            href=str(site_href),
        )
    )
    site_link.add(raw(str(site_html)))
    left_column.add(raw(". "))
    left_column.add(raw(str(rights_html)))

    right_column = row.add(tags.div(_class="col-12 col-md-auto"))
    email_link = right_column.add(
        tags.a(_class="fw-semibold", href=str(email_href))
    )
    email_link.add(raw(str(email_html)))

    return Markup(footer_tag.render())
