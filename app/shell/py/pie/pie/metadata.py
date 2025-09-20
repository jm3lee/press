#!/usr/bin/env python3
"""Helpers for loading and retrieving document metadata."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
from urllib.parse import urljoin

import redis
from flatten_dict import unflatten
from pie.logging import logger
from pie.yaml import YAML_EXTS, read_yaml, yaml
from ruamel.yaml import YAMLError
from pie.schema import DEFAULT_SCHEMA


def get_url(filename: str) -> Optional[str]:
    """Compute the HTML URL for a given Markdown or YAML source file.

    Source files under ``src/`` map to HTML paths. For example::

        src/guide/intro.md         -> /guide/intro.html
        src/config/settings.yaml   -> /config/settings.html

    Args:
        filename: Path to the source file, expected to start with ``src/``.

    Returns:
        A URL string starting with ``/`` and ending with ``.html``, or ``None``
        if the filename does not start with ``src/`` or has an unsupported
        extension.
    """
    prefix = "src" + os.sep
    if filename.startswith(prefix):
        relative_path = filename[len(prefix) :]
        base, ext = os.path.splitext(relative_path)
        if ext.lower() in {".md", ".mdi"} | YAML_EXTS:
            html_path = base + ".html"
            return "/" + html_path
    prefix = "build" + os.sep
    if filename.startswith(prefix):
        relative_path = filename[len(prefix) :]
        base, ext = os.path.splitext(relative_path)
        if ext.lower() in {".md", ".mdi"} | YAML_EXTS:
            html_path = base + ".html"
            return "/" + html_path
    logger.warning("Can't create a url.", filename=filename)
    raise Exception("Can't create a url.")


def get_frontmatter(filename: str) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from a Markdown file."""

    with open(filename, encoding="utf-8") as file:
        lines = file.readlines()

    if not lines or lines[0].strip() != "---":
        return None

    yaml_lines = []
    # Skip the first '---'
    for line in lines[1:]:
        if line.strip() == "---":
            break
        yaml_lines.append(line)

    content = "".join(yaml_lines)
    return yaml.load(content)


def _add_url_if_missing(metadata: dict[str, Any], filepath: str) -> None:
    """Assign a ``url`` derived from ``filepath`` if absent."""

    if "url" not in metadata:
        metadata["url"] = get_url(filepath)


def _add_citation_if_missing(metadata: dict[str, Any], filepath: str) -> None:
    """Derive ``doc.citation`` from ``doc.title`` or deprecated ``name``."""

    doc = metadata.setdefault("doc", {})
    if "citation" not in doc:
        title = doc.get("title") or metadata.get("title")
        if title:
            doc["citation"] = title.lower()
        elif "name" in metadata:
            logger.warning(
                "'name' field is deprecated; use 'title' instead",
                filename=filepath,
            )
            doc["citation"] = metadata["name"].lower()


def _add_id_if_missing(metadata: dict[str, Any], filepath: str) -> None:
    """Generate an ``id`` based on ``filepath`` if absent."""

    if "id" not in metadata:
        base = Path(filepath).with_suffix("")
        metadata["id"] = base.name
        logger.debug(
            "Generated 'id'",
            filename=str(Path(filepath).resolve().relative_to(Path.cwd())),
            id=metadata["id"],
        )


def _add_canonical_link_if_missing(metadata: dict[str, Any], filepath: str) -> None:
    """Create ``doc.link.canonical`` from ``url`` when missing."""

    doc = metadata.get("doc")
    if isinstance(doc, dict):
        link = doc.get("link")
        if isinstance(link, dict) and link.get("canonical"):
            return

    url = metadata.get("url")
    if url is None:
        logger.debug("Skipping canonical link; no url present", filename=filepath)
        return

    base_url = os.getenv("BASE_URL", "").rstrip("/")
    canonical = urljoin(base_url + "/", url.lstrip("/")) if base_url else url

    metadata.setdefault("doc", {}).setdefault("link", {})["canonical"] = canonical


def _add_if_missing(
    metadata: dict[str, Any], field: str, value: Any, filepath: str
) -> None:
    """Assign ``value`` to ``field`` when it is missing.

    ``field`` may be a dotted path such as ``foo.bar``.
    """

    parts = field.split(".")
    obj: dict[str, Any] = metadata
    for part in parts[:-1]:
        sub = obj.get(part)
        if not isinstance(sub, dict):
            sub = {}
            obj[part] = sub
        obj = sub
    last = parts[-1]
    if last not in obj:
        obj[last] = value
        logger.debug(
            "Generated",
            id=metadata.get("id"),
            field=field,
            filename=str(Path(filepath).resolve().relative_to(Path.cwd())),
        )

def generate_missing_metadata(
    metadata: dict[str, Any], filepath: str
) -> dict[str, Any]:
    """Populate ``metadata`` with fields derived from ``filepath`` if absent."""

    _add_url_if_missing(metadata, filepath)
    _add_canonical_link_if_missing(metadata, filepath)
    _add_citation_if_missing(metadata, filepath)
    _add_id_if_missing(metadata, filepath)
    _add_if_missing(metadata, 'doc.breadcrumbs', None, filepath)
    _add_if_missing(metadata, 'css', ['/css/style.css'], filepath)
    _add_if_missing(metadata, 'description', None, filepath)
    _add_if_missing(metadata, 'doc.mathjax', False, filepath)
    _add_if_missing(metadata, 'header', {'header': None}, filepath)
    _add_if_missing(metadata, 'html', {'scripts': []}, filepath)
    _add_if_missing(metadata, 'next', None, filepath)
    _add_if_missing(metadata, 'og_description', None, filepath)
    _add_if_missing(metadata, 'og_image', None, filepath)
    _add_if_missing(metadata, 'og_title', None, filepath)
    _add_if_missing(metadata, 'og_url', None, filepath)
    _add_if_missing(metadata, 'page_heading', None, filepath)
    _add_if_missing(metadata, 'partof', None, filepath)
    _add_if_missing(metadata, 'preamble', None, filepath)
    _add_if_missing(metadata, 'prev', None, filepath)
    _add_if_missing(metadata, 'doc.pubdate', None, filepath)
    _add_if_missing(metadata, 'schema', DEFAULT_SCHEMA, filepath)
    _add_if_missing(metadata, 'status', None, filepath)
    _add_if_missing(metadata, 'toc', None, filepath)
    _add_if_missing(metadata, 'twitter_card', None, filepath)
    _add_if_missing(metadata, 'twitter_image', None, filepath)
    logger.debug("returning", metadata=metadata)
    return metadata


def _read_from_markdown(filepath: str) -> Optional[Dict[str, Any]]:
    """Load metadata from a Markdown file without adding defaults.

    ``generate_missing_metadata`` should be called by the caller if default
    fields such as ``url`` or ``id`` are required.
    """

    metadata = get_frontmatter(filepath)
    if metadata is None:
        logger.debug("No frontmatter found in Markdown file", filename=filepath)
        return None
    return metadata


def read_from_yaml(filepath: str) -> Optional[Dict[str, Any]]:
    """Load and validate metadata from a YAML file without adding defaults.

    ``generate_missing_metadata`` should be called by the caller if additional
    fields derived from ``filepath`` are needed.
    """

    try:
        return read_yaml(filepath)
    except YAMLError as err:
        logger.error("Failed to parse YAML file", filepath=filepath)
        err.add_note(f"file: {filepath}")
        logger.error(err)
        raise


# Global connection reused by helper functions.  It is initialised lazily so
# unit tests can swap in a fake client.
redis_conn: redis.Redis | None = None


def _get_conn() -> redis.Redis:
    """Return a Redis connection using environment configuration.

    Examples
    --------
    >>> conn = _get_conn()
    >>> isinstance(conn, redis.Redis)
    True
    """

    global redis_conn
    if redis_conn is None:
        host = os.getenv("REDIS_HOST", "dragonfly")
        port = int(os.getenv("REDIS_PORT", "6379"))
        redis_conn = redis.Redis(host=host, port=port, decode_responses=True)
    return redis_conn


def _get_redis_value(key: str, *, required: bool = False):
    """Return the decoded value for ``key`` from Redis.

    Examples
    --------
    >>> conn = _get_conn()
    >>> conn.set("example", "1")
    True
    >>> _get_redis_value("example")
    1
    """

    conn = _get_conn()
    try:
        val = conn.get(key)
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
    """Recursively convert dictionaries with integer keys to lists.

    Example
    -------
    >>> _convert_lists({"0": "a", "2": {"0": "b"}})
    ['a', None, ['b']]
    """

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


def build_from_redis(prefix: str) -> dict | list | None:
    """Return a nested structure for all keys starting with ``prefix``.

    Example
    -------
    >>> conn = _get_conn()
    >>> conn.mset({"entry.1.title": '"Hi"'})
    True
    >>> build_from_redis("entry.")
    {'1': {'title': 'Hi'}}
    """

    conn = _get_conn()

    keys = conn.keys(prefix + "*")
    if not keys:
        return None

    flat = {}
    for k in keys:
        val = _get_redis_value(k, required=True)
        flat[k[len(prefix) :].lstrip(".")] = val

    data = unflatten(flat, splitter="dot")
    return _convert_lists(data)


_metadata_cache: dict[str, dict[str, Any]] = {}


def get_metadata(name: str) -> dict[str, Any] | None:
    """Return metadata dictionary for ``name`` from Redis."""

    return build_from_redis(f"{name}.")


def get_cached_metadata(key: str) -> dict[str, Any]:
    """Return cached metadata for ``key``.

    Metadata is looked up from Redis on the first request and stored in a
    module-level cache. Subsequent lookups reuse the cached value.
    """

    if key not in _metadata_cache:
        data: dict[str, Any] | None = None
        for _ in range(3):
            data = get_metadata(key)
            if data is not None:
                break
            time.sleep(0.5)
        if data is None:
            logger.error("Missing metadata", id=key)
            raise SystemExit(1)
        _metadata_cache[key] = data
    return _metadata_cache[key]


def clear_cached_metadata() -> None:
    """Reset the metadata cache used by :func:`get_cached_metadata`."""

    _metadata_cache.clear()


def get_metadata_by_path(filepath: str, keypath: str) -> Any | None:
    """Return metadata value for ``keypath`` associated with ``filepath``.

    The function first looks up the document ``id`` stored under ``filepath``
    in Redis and then retrieves ``<id>.<keypath>``.
    """

    conn = _get_conn()

    doc_id = conn.get(filepath)
    if not doc_id:
        logger.warning("unknown metadata", filepath=filepath, keypath=keypath)
        return None
    return conn.get(f"{doc_id}.{keypath}")


def load_metadata_pair(path: Path) -> Mapping[str, Any] | None:
    """Load metadata from ``path`` and a sibling Markdown or metadata file.

    If both a ``.md``/``.mdi`` and ``.yml``/``.yaml`` exist for the same base
    name, the metadata from each file is combined. Values from YAML override
    those from Markdown when keys conflict and a :class:`UserWarning` is
    emitted. Returns ``None`` if neither file contains metadata.

    Example
    -------
    >>> (tmp / 'post.md').write_text('---\ntitle: Draft\n---\n')
    17
    >>> (tmp / 'post.yml').write_text('title: Example')
    17
    >>> load_metadata_pair(tmp / 'post.yml')
    {'title': 'Example', 'id': 'post', 'path': ['post.yml', 'post.md']}
    """

    base = path.with_suffix("")
    md_path = base.with_suffix(".md")
    mdi_path = base.with_suffix(".mdi")
    yml_path = base.with_suffix(".yml")
    yaml_path = base.with_suffix(".yaml")

    md_data = None
    markdown_file: Path | None = None
    if md_path.exists():
        markdown_file = md_path
    elif mdi_path.exists():
        markdown_file = mdi_path
    if markdown_file:
        md_data = _read_from_markdown(str(markdown_file))

    meta_data = None
    meta_file: Path | None = None
    if yml_path.exists():
        meta_file = yml_path
        meta_data = read_from_yaml(str(yml_path))
    elif yaml_path.exists():
        meta_file = yaml_path
        meta_data = read_from_yaml(str(yaml_path))

    if md_data is None and meta_data is None:
        return None

    combined: dict[str, Any] = {}
    if md_data:
        combined.update(md_data)
    if meta_data:
        for k, v in meta_data.items():
            if k in combined and combined[k] != v:
                logger.warning(
                    "Conflict for '{}', using value from {}",
                    k,
                    meta_file.resolve().relative_to(Path.cwd()),
                )
            combined[k] = v

    files: list[Path] = []
    if meta_file:
        files.append(meta_file)
    if markdown_file:
        files.append(markdown_file)

    if files:
        combined["path"] = [
            str(p.resolve().relative_to(Path.cwd())) for p in files
        ]
    # Populate any missing metadata fields based on the source path.
    source = markdown_file or meta_file or path
    combined = generate_missing_metadata(combined, str(source))

    logger.debug("returning", combined=combined)
    return combined
