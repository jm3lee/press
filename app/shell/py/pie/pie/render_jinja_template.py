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

import redis
import yaml
from flatten_dict import unflatten
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pie.utils import logger, read_json, read_utf8, add_log_argument, setup_file_logger

DEFAULT_CONFIG = Path("cfg/render-jinja-template.yml")

index_json = None  # Loaded in :func:`main`.
config = {}
redis_conn = None  # lazily initialised connection used by ``linktitle``.

_whitespace_word_pattern = re.compile(r"(\S+)")


def _get_redis_value(key: str, *, required: bool = False):
    """Return the decoded value for ``key`` from ``redis_conn``.

    If ``required`` is ``True`` and the key is missing, the process exits
    with status 1 after logging an error.
    """

    global redis_conn
    if redis_conn is None:
        host = os.getenv("REDIS_HOST", "dragonfly")
        port = int(os.getenv("REDIS_PORT", "6379"))
        redis_conn = redis.Redis(host=host, port=port, decode_responses=True)
    try:
        val = redis_conn.get(key)
    except Exception as exc:
        logger.error("Redis lookup failed", key=key, exception=str(exc))
        raise SystemExit(1)

    if val is None:
        if required:
            logger.error("Missing metadata", key=key)
            raise SystemExit(1)
        return None

    try:
        return json.loads(val)
    except Exception:
        return val


def _convert_lists(obj):
    """Recursively convert dictionaries with integer keys to lists."""

    if isinstance(obj, dict):
        if obj and all(isinstance(k, str) and k.isdigit() for k in obj):
            arr = [None] * (max(int(k) for k in obj) + 1)
            for k, v in obj.items():
                arr[int(k)] = _convert_lists(v)
            return arr
        return {k: _convert_lists(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_lists(v) for v in obj]
    return obj


def _build_from_redis(prefix: str) -> dict | list | None:
    """Return a nested structure for all keys starting with ``prefix``."""

    global redis_conn
    if redis_conn is None:
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        redis_conn = redis.Redis(host=host, port=port, decode_responses=True)

    keys = redis_conn.keys(prefix + "*")
    if not keys:
        return None

    flat = {}
    for k in keys:
        val = _get_redis_value(k, required=True)
        flat[k[len(prefix) :].lstrip(".")] = val

    data = unflatten(flat, splitter="dot")
    return _convert_lists(data)


def _get_metadata(name: str) -> dict | None:
    """Return metadata dictionary for ``name`` from Redis."""

    return _build_from_redis(f"{name}.")


def _load_desc(desc):
    """Return a metadata dict for ``desc`` using Redis lookups when needed."""

    if isinstance(desc, str):
        data = None
        for _ in range(3):
            data = _get_metadata(desc)
            if data is not None:
                break
            time.sleep(0.5)
        if data is None:
            logger.error("Missing metadata", id=desc)
            raise SystemExit(1)
        return data
    if not isinstance(desc, dict):
        logger.error("Invalid descriptor type", type=str(type(desc)))
        raise SystemExit(1)
    return desc


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
    looked up via :func:`_load_desc`.  ``style`` controls how the citation text
    is capitalised: ``"plain"`` leaves it untouched, ``"title"`` applies
    title‑case, and ``"cap"`` capitalises only the first character.  When
    ``use_icon`` is ``True`` any ``icon`` field is prefixed to the citation.
    ``citation`` selects which citation field to use; pass ``"short"`` to use
    ``citation["short"]``.
    """

    desc = _load_desc(desc)

    # Determine citation text
    citation_val = desc["citation"]
    if citation == "short":
        citation_text = citation_val["short"]
    else:
        if isinstance(citation_val, dict):
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
        with cfg_path.open("r", encoding="utf-8") as cf:
            return yaml.safe_load(cf) or {}
    except Exception as exc:
        logger.error(
            "Failed to load configuration", path=str(cfg_path), exception=str(exc)
        )
        raise SystemExit(1)


def create_env():
    """Create and configure the Jinja2 environment."""

    env = Environment(loader=FileSystemLoader("/data"), undefined=StrictUndefined)
    env.filters["link"] = render_link
    env.filters["linktitle"] = linktitle
    env.filters["linkcap"] = linkcap
    env.filters["link_icon_title"] = link_icon_title
    env.filters["linkicon"] = linkicon
    env.filters["linkshort"] = linkshort
    env.filters["get_desc"] = get_desc
    env.globals["render_jinja"] = render_jinja
    env.globals["to_alpha_index"] = to_alpha_index
    env.globals["read_json"] = read_json
    env.globals["read_yaml"] = read_yaml
    return env


env = create_env()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Render a template using metadata from Redis and an optional index file",
    )
    parser.add_argument("template", help="Template file to render")
    parser.add_argument(
        "-i",
        "--index",
        help="Optional path to index.json",
    )
    add_log_argument(parser)
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

    setup_file_logger(args.log)

    global config
    config = load_config(args.config)
    index_json = read_json(args.index) if args.index else {}
    template = env.get_template(args.template)
    print(template.render(**index_json))


if __name__ == "__main__":
    main()
