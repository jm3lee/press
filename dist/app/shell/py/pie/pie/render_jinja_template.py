#!/usr/bin/env python3

"""Helper filters and globals for rendering Jinja templates.

This module exposes a set of Jinja2 filters and global functions used by the
press build scripts.  It can also be executed as a small CLI to render a
template using variables loaded from ``index.json``.
"""

import json
import os
import re
import sys
import argparse
import warnings

import redis

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from xmera.utils import read_json, read_utf8
from pie.utils import add_file_logger, logger

index_json = None  # Loaded in :func:`main`.
redis_conn = None  # lazily initialised connection used by ``linktitle``.

_whitespace_word_pattern = re.compile(r"(\S+)")


def _get_redis_value(key: str):
    """Return the decoded value for ``key`` from ``redis_conn`` or ``None``."""

    global redis_conn
    if redis_conn is None:
        host = os.getenv("REDIS_HOST", "dragonfly")
        port = int(os.getenv("REDIS_PORT", "6379"))
        redis_conn = redis.Redis(host=host, port=port, decode_responses=True)
    try:
        val = redis_conn.get(key)
    except Exception:
        return None
    if val is None:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val


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


def linktitle(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).

    ``update-index`` inserts metadata into Redis with keys of the form
    ``<id>.<property>``. When ``desc`` is a string, this function now looks up
    the relevant fields in Redis. If the values are missing, ``index.json`` is
    consulted as a fallback and a :class:`UserWarning` is emitted.
    """

    if isinstance(desc, str):
        name = desc
        desc = {}
        citation = _get_redis_value(f"{name}.citation")
        url = _get_redis_value(f"{name}.url")
        icon = _get_redis_value(f"{name}.icon")
        link_class = _get_redis_value(f"{name}.link.class")
        tracking = _get_redis_value(f"{name}.link.tracking")
        if citation is not None:
            desc["citation"] = citation
        if url is not None:
            desc["url"] = url
        if icon is not None:
            desc["icon"] = icon
        link_opts = {}
        if link_class is not None:
            link_opts["class"] = link_class
        if tracking is not None:
            link_opts["tracking"] = tracking
        if link_opts:
            desc["link"] = link_opts

        fallback = index_json.get(name) if index_json else None
        if fallback and ("citation" not in desc or "url" not in desc):
            warnings.warn(
                f"Missing redis data for '{name}', using index.json fallback",
                UserWarning,
            )
            for key in ("citation", "url", "icon", "link"):
                if key in fallback and key not in desc:
                    desc[key] = fallback[key]

    if not isinstance(desc, dict):
        return desc

    citation = desc["citation"]
    url = desc["url"]
    icon = desc.get("icon")
    a_attribs = get_tracking_options(desc)

    def cap_match(m):
        word = m.group(1)
        if word in ("of",):
            return word
        return word[0].upper() + word[1:]

    citation = _whitespace_word_pattern.sub(cap_match, citation)

    if icon:
        return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{icon} {citation}</a>"""
    return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{citation}</a>"""


def link_icon_title(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    citation = desc["citation"]
    url = desc["url"]
    icon = desc["icon"]
    a_attribs = get_tracking_options(desc)

    def cap_match(m):
        word = m.group(1)
        return word[0].upper() + word[1:]

    citation = _whitespace_word_pattern.sub(cap_match, citation)
    return (
        f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{icon} {citation}</a>"""
    )


def linkcap(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    if not isinstance(desc, dict):
        return desc

    citation = desc["citation"]
    citation = citation[0].upper() + citation[1:]
    url = desc["url"]
    icon = desc.get("icon")
    a_attribs = get_tracking_options(desc)
    if icon:
        return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{icon} {citation}</a>"""
    return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{citation}</a>"""


def linkicon(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    citation = desc["citation"]
    url = desc["url"]
    icon = desc.get("icon")
    a_attribs = get_tracking_options(desc)
    if icon:
        return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{icon} {citation}</a>"""
    return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{citation}</a>"""


def link(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    citation = desc["citation"]
    url = desc["url"]
    a_attribs = get_tracking_options(desc)
    return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{citation}</a>"""


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
                logger.warning(
                    "No front matter or title", file=full_path
                )


def get_origins(name):
    """Yield origin references for the given entry ``name``."""

    j = index_json[name]
    for i in j["origins"]:
        if i in index_json:
            yield index_json[i]
        else:
            yield i


def get_insertions(name):
    """Yield insertion references for ``name``."""

    j = index_json[name]
    for i in j["insertions"]:
        if i in index_json:
            yield index_json[i]
        else:
            yield i


def get_actions(name):
    """Yield actions associated with ``name`` from ``index_json``."""

    j = index_json[name]
    yield from j["actions"]


def get_translations(name):
    """Yield key/value translation pairs for ``name``."""

    j = index_json[name]
    yield from j["translations"].items()


def get_desc(name):
    """Return the metadata entry for ``name`` or ``name`` itself."""

    d = index_json.get(name)
    if d:
        return d
    return name


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


def create_env():
    """Create and configure the Jinja2 environment."""

    env = Environment(loader=FileSystemLoader("/data"), undefined=StrictUndefined)
    env.filters["link"] = link
    env.filters["linktitle"] = linktitle
    env.filters["linkcap"] = linkcap
    env.filters["link_icon_title"] = link_icon_title
    env.filters["linkicon"] = linkicon
    env.filters["get_desc"] = get_desc
    env.globals["get_origins"] = get_origins
    env.globals["get_insertions"] = get_insertions
    env.globals["get_actions"] = get_actions
    env.globals["get_translations"] = get_translations
    env.globals["render_jinja"] = render_jinja
    env.globals["to_alpha_index"] = to_alpha_index
    env.globals["read_json"] = read_json
    env.globals["read_yaml"] = read_yaml
    return env


env = create_env()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Render a template using variables from an index JSON file",
    )
    parser.add_argument("index", help="Path to index.json")
    parser.add_argument("template", help="Template file to render")
    parser.add_argument(
        "-l",
        "--log",
        help="Write logs to the specified file",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Render the specified template using variables from ``index.json``."""

    global index_json
    args = parse_args(argv)

    if args.log:
        add_file_logger(args.log, level="DEBUG")

    index_json = read_json(args.index)
    template = env.get_template(args.template)
    print(template.render(**index_json))


if __name__ == "__main__":
    main()
