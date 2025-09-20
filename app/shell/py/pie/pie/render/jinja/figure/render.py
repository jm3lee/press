"""Render helpers for ``<figure>`` elements in Jinja templates."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Any

from pie.logging import logger

MetadataResolver = Callable[[str], dict[str, Any]]

_metadata_resolver: MetadataResolver | None = None


def set_metadata_resolver(resolver: MetadataResolver | None) -> None:
    """Configure the callable used to resolve metadata ids."""

    global _metadata_resolver
    _metadata_resolver = resolver


def _get_cached_metadata(key: str) -> dict[str, Any]:
    """Return metadata for ``key`` using the configured resolver."""

    if _metadata_resolver is None:
        from pie.metadata import get_cached_metadata as default_resolver

        return default_resolver(key)
    return _metadata_resolver(key)


def _extend_srcset(parts: list[str], urls: Iterable[Any]) -> None:
    """Append formatted ``srcset`` entries from ``urls`` to ``parts``."""

    for entry in urls:
        if isinstance(entry, dict):
            url = entry.get("url")
            width = entry.get("width")
            descriptor = f" {width}w" if width else ""
            parts.append(f"{url}{descriptor}")
        else:
            parts.append(str(entry))


def render(desc: str | dict[str, Any]) -> str:
    """Return an HTML ``<figure>`` block for ``desc``.

    ``desc`` may be either a metadata dictionary or a string key which will be
    resolved via :func:`pie.metadata.get_cached_metadata`.
    """

    if isinstance(desc, str):
        desc = _get_cached_metadata(desc)
    elif not isinstance(desc, dict):
        logger.error("Invalid descriptor type", type=str(type(desc)))
        raise SystemExit(1)

    title = desc.get("title", "")
    fig = desc.get("figure", {})
    caption = fig.get("caption", title)
    src = desc.get("url")

    srcset_parts: list[str] = []

    urls = fig.get("urls")
    if urls:
        if isinstance(urls, (list, tuple, set)):
            _extend_srcset(srcset_parts, urls)
        else:
            if isinstance(urls, dict):
                _extend_srcset(srcset_parts, [urls])
            else:
                srcset_parts.append(str(urls))
    else:
        widths = fig.get("widths")
        if widths:
            pattern = fig.get("pattern")
            if not pattern:
                if src and "{width}" in src:
                    pattern = src
                else:
                    pattern = re.sub(r"\d+", "{width}", src or "", count=1)
            for width in widths:
                srcset_parts.append(f"{pattern.format(width=width)} {width}w")
            if not src:
                src = pattern.format(width=widths[0])

    srcset_attr = f' srcset="{", ".join(srcset_parts)}"' if srcset_parts else ""

    sizes = fig.get("sizes")
    sizes_attr = f' sizes="{sizes}"' if sizes and srcset_parts else ""

    return (
        '<figure class="figure">'
        f'<img src="{src}"{srcset_attr}{sizes_attr} alt="{title}" '
        'class="figure-img img-fluid rounded" loading="lazy"/>'
        f'<figcaption class="figure-caption tex-center">{caption}</figcaption>'
        "</figure>"
    )


__all__ = ["render", "set_metadata_resolver"]
