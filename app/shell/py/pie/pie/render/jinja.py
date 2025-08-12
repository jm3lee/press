#!/usr/bin/env python3

"""Helper filters and globals for rendering Jinja templates.

This module exposes a set of Jinja2 filters and global functions used by the
press build scripts.  It can also be executed as a small CLI to render a
template. Metadata is loaded from Redis and an optional ``index.json`` file.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pie.cli import create_parser
from pie.logging import logger, configure_logging
from pie.utils import read_json, read_utf8, write_utf8, read_yaml as load_yaml_file
from pie import metadata

DEFAULT_CONFIG = Path("cfg/render-jinja-template.yml")

index_json = None  # Loaded in :func:`main`.
config = {}

_whitespace_word_pattern = re.compile(r"(\S+)")

def _get_metadata(name: str) -> dict | None:
    """Return metadata dictionary for ``name`` from Redis."""

    return metadata.build_from_redis(f"{name}.")

_metadata_cache: dict[str, dict] = {}

def get_cached_metadata(key: str) -> dict:
    """Return cached metadata for ``key``.

    Metadata is looked up from Redis on the first request and stored in a
    module‑level cache. Subsequent lookups reuse the cached value.
    """

    if key not in _metadata_cache:
        data = None
        for _ in range(3):
            data = _get_metadata(key)
            if data is not None:
                break
            time.sleep(0.5)
        if data is None:
            logger.error("Missing metadata", id=key)
            raise SystemExit(1)
        _metadata_cache[key] = data
    return _metadata_cache[key]

def get_tracking_options(desc):
    """Return HTML attributes for link tracking behaviour.

    The metadata dictionary ``desc`` may contain ``link.tracking``. When this
    value is ``False`` the returned string includes ``rel`` and ``target``
    attributes so external links open in a new tab without leaking referrer
    information.  Otherwise an empty string is returned.
    """

    link = desc.get("link")
    if link is not None:
        tracking = link.get("tracking")
        if not tracking:
            return 'rel="noopener noreferrer" target="_blank"'
    return ""

def get_link_class(desc):
    """Return the CSS class to use for a link."""

    if "link" in desc:
        link_options = desc["link"]
        if isinstance(link_options, dict) and "class" in link_options:
            return link_options["class"]
    return "internal-link"

def render_link(
    desc,
    *,
    style: str = "plain",
    use_icon: bool = True,
    citation: str = "citation",
    anchor: str | None = None,
):
    """Return a formatted HTML anchor for ``desc``.

    ``desc`` may be either a metadata dictionary or a string id which will be
    looked up via :func:`get_cached_metadata`.  ``style`` controls how the
    citation text is capitalised: ``"plain"`` leaves it untouched, ``"title"``
    applies title‑case, and ``"cap"`` capitalises only the first character.
    When ``use_icon`` is ``True`` any ``icon`` field is prefixed to the
    citation. ``citation`` selects which citation field to use; pass
    ``"short"`` to use ``citation["short"]``.
    """

    if isinstance(desc, str):
        desc = get_cached_metadata(desc)
    elif not isinstance(desc, dict):
        logger.error("Invalid descriptor type", type=str(type(desc)))
        raise SystemExit(1)

    # Determine citation text
    citation_val = desc["citation"]
    needs_parens = False
    if citation == "short":
        citation_text = citation_val["short"]
    else:
        if isinstance(citation_val, dict):
            if {"author", "year"}.issubset(citation_val):
                author = str(citation_val.get("author", "")).title()
                year = citation_val.get("year")
                pages = citation_val.get("page")
                citation_text = author
                if year is not None:
                    citation_text += f" {year}"
                if pages:
                    if isinstance(pages, (list, tuple)):
                        pages = ", ".join(str(p) for p in pages)
                    citation_text += f", {pages}"
                needs_parens = True
            else:
                citation_text = citation_val.get(citation)
        else:
            citation_text = citation_val

    # Apply requested capitalisation style
    if style == "title":
        def cap_match(m):
            word = m.group(1)
            if word.lower() in {"of", "in", "a", "an"}:
                return word
            return word[0].upper() + word[1:]

        citation_text = _whitespace_word_pattern.sub(cap_match, citation_text)
    elif style == "cap" and citation_text:
        citation_text = citation_text[0].upper() + citation_text[1:]

    if needs_parens:
        citation_text = f"({citation_text})"

    url = desc["url"]
    if anchor:
        url += anchor if anchor.startswith("#") else f"#{anchor}"
    icon = desc.get("icon") if use_icon else None
    a_attribs = get_tracking_options(desc)

    if icon:
        return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{icon} {citation_text}</a>"""
    return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{citation_text}</a>"""

def linktitle(desc, anchor: str | None = None):
    return render_link(desc, style="title", anchor=anchor)

def link_icon_title(desc, anchor: str | None = None):
    return render_link(desc, style="title", use_icon=True, anchor=anchor)

def linkcap(desc, anchor: str | None = None):
    return render_link(desc, style="cap", anchor=anchor)

def linkicon(desc, anchor: str | None = None):
    return render_link(desc, use_icon=True, anchor=anchor)

def link(desc, anchor: str | None = None):
    return render_link(desc, use_icon=False, anchor=anchor)

def linkshort(desc, anchor: str | None = None):
    return render_link(desc, use_icon=False, citation="short", anchor=anchor)

def cite(*names: str) -> str:
    """Return Chicago style citation links for ``names``.

    Each ``name`` is looked up using :func:`get_cached_metadata`. ``citation`` may be a
    simple string (legacy format) or a mapping with ``author``, ``year`` and
    ``page`` keys.  When multiple references share the same author, year and
    URL their page numbers are combined.

    When a single reference is provided the parentheses are included inside the
    returned anchor.  Multiple references are separated by ``;`` with the outer
    parentheses wrapping the entire group.
    """

    descs = [get_cached_metadata(n) if isinstance(n, str) else n for n in names]

    groups: list[dict] = []
    for d in descs:
        cit = d.get("citation")
        if isinstance(cit, dict):
            author = str(cit.get("author", "")).title()
            year = cit.get("year")
            page = cit.get("page")
            key = (author, year, d.get("url"))
            for g in groups:
                if g.get("key") == key:
                    g["pages"].append(page)
                    break
            else:
                groups.append({
                    "key": key,
                    "author": author,
                    "year": year,
                    "pages": [page],
                    "desc": d,
                })
        else:
            groups.append({"text": cit, "desc": d})

    parts: list[str] = []
    single = len(groups) == 1
    for g in groups:
        desc = dict(g["desc"])
        if "text" in g:
            text = g["text"]
        else:
            pages = ", ".join(str(p) for p in g["pages"] if p is not None)
            text = f"{g['author']} {g['year']}"
            if pages:
                text += f", {pages}"
        if single:
            desc["citation"] = f"({text})"
            return render_link(desc, use_icon=False)
        desc["citation"] = text
        parts.append(render_link(desc, use_icon=False))

    return "(" + "; ".join(parts) + ")"

def extract_front_matter(file_path: str) -> dict | None:
    """
    Read a Markdown file and return its YAML front matter as a dict,
    or None if there's no valid front matter block.
    """
    front_matter_lines = []
    in_block = False

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() == "---":
                if not in_block:
                    in_block = True
                else:
                    # closing delimiter
                    break
            elif in_block:
                front_matter_lines.append(line)

    if in_block and front_matter_lines:
        try:
            return yaml.safe_load("".join(front_matter_lines))
        except yaml.YAMLError:
            return None
    return None

def process_directory(root_dir: str) -> None:
    """
    Walk `root_dir` recursively, find all .md files, and:
      - If front matter exists and has a 'title', print:
          TITLE: <title> | FILE: <path>
      - Otherwise, write a warning to stderr.
    """
    for dirpath, _, files in os.walk(root_dir):
        for fname in files:
            if not fname.lower().endswith(".md"):
                continue

            full_path = os.path.join(dirpath, fname)
            fm = extract_front_matter(full_path)

            if fm and isinstance(fm, dict) and "title" in fm:
                logger.info(
                    "TITLE: {title} | FILE: {file}",
                    title=fm["title"],
                    file=full_path,
                )
            else:
                logger.warning("No front matter or title", file=full_path)

def get_desc(name):
    """Return the metadata entry for ``name`` from Redis."""

    d = _get_metadata(name)
    if d is None:
        logger.error("Metadata not found", id=name)
        raise SystemExit(1)
    return d

def render_jinja(snippet):
    """Render a Jinja snippet using the current environment."""

    logger.info(snippet)
    return env.from_string(snippet).render(**index_json)

def to_alpha_index(i):
    """Convert ``0``–``3`` to ``a``–``d``."""

    return ("a", "b", "c", "d")[i]

def read_yaml(filename):
    """Read ``filename`` as YAML and yield the ``toc`` sequence."""

    y = yaml.safe_load(read_utf8(filename))
    logger.info(y["toc"])
    yield from y["toc"]

def load_config(path: str | Path = DEFAULT_CONFIG) -> dict:
    """Load configuration from *path* and return a dict."""

    cfg_path = Path(path)
    if not cfg_path.exists():
        if cfg_path == DEFAULT_CONFIG:
            return {}
        logger.error("Configuration file not found", path=str(cfg_path))
        raise SystemExit(1)
    try:
        return load_yaml_file(str(cfg_path)) or {}
    except Exception as exc:
        logger.error(
            "Failed to load configuration", path=str(cfg_path), exception=str(exc)
        )
        raise SystemExit(1)

def create_env():
    """Create and configure the Jinja2 environment."""

    env = Environment(loader=FileSystemLoader("/data"), undefined=StrictUndefined)
    env.globals["link"] = render_link
    env.globals["linktitle"] = linktitle
    env.globals["linkcap"] = linkcap
    env.globals["link_icon_title"] = link_icon_title
    env.globals["linkicon"] = linkicon
    env.globals["linkshort"] = linkshort
    env.filters["get_desc"] = get_desc
    env.globals["render_jinja"] = render_jinja
    env.globals["to_alpha_index"] = to_alpha_index
    env.globals["read_json"] = read_json
    env.globals["read_yaml"] = read_yaml
    env.globals["cite"] = cite
    return env

env = create_env()

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = create_parser(
        "Render a template using metadata from Redis and an optional index file"
    )
    parser.add_argument("template", help="Template file to render")
    parser.add_argument("output", help="File to write rendered template to")
    parser.add_argument(
        "-i",
        "--index",
        help="Optional path to index.json",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Path to YAML configuration file",
    )
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> None:
    """Render the specified template using Redis and an optional ``index.json``."""

    global index_json
    args = parse_args(argv)

    configure_logging(args.verbose, args.log)

    global config
    config = load_config(args.config)
    index_json = read_json(args.index) if args.index else {}
    template = env.get_template(args.template)
    rendered = template.render(**index_json)
    write_utf8(rendered, args.output)

if __name__ == "__main__":
    main()
