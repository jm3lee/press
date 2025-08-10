#!/usr/bin/env python3
"""Helpers for loading and retrieving document metadata."""

from __future__ import annotations

import json
import os
import warnings
from pathlib import Path
from typing import Any, Mapping

import redis
import yaml
from flatten_dict import unflatten

from pie.logging import logger
from pie.utils import read_yaml

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


def get_metadata_by_path(filepath: str, keypath: str) -> Any | None:
    """Return metadata value for ``keypath`` associated with ``filepath``.

    The function first looks up the document ``id`` stored under ``filepath``
    in Redis and then retrieves ``<id>.<keypath>``.

    Example
    -------
    >>> conn = _get_conn()
    >>> conn.mset({"doc.md": "123", "123.title": '"Doc"'})
    True
    >>> get_metadata_by_path("doc.md", "title")
    'Doc'
    """

    conn = _get_conn()

    doc_id = conn.get(filepath)
    if not doc_id:
        return None
    return conn.get(f"{doc_id}.{keypath}")


def fill_missing_metadata(
    metadata: dict[str, Any], *, filepath: str | None = None, doc_id: str | None = None
) -> dict[str, Any]:
    """Populate ``id``, ``url``, and ``citation`` fields when absent."""

    if filepath and "url" not in metadata:
        from pie import build_index

        metadata["url"] = build_index.get_url(filepath)
        logger.debug("Generated 'url'", filename=filepath, url=metadata["url"])

    if "citation" not in metadata and "name" in metadata:
        metadata["citation"] = metadata["name"].lower()
        logger.debug("Generated 'citation'", citation=metadata["citation"])

    if "id" not in metadata:
        if doc_id:
            metadata["id"] = doc_id
            logger.debug("Generated 'id'", id=metadata["id"])
        elif filepath:
            base, _ = os.path.splitext(filepath)
            metadata["id"] = base.split(os.sep)[-1]
            logger.debug("Generated 'id'", filename=filepath, id=metadata["id"])

    return metadata


def get_frontmatter(filename: str) -> dict[str, Any] | None:
    """Extract YAML frontmatter from a Markdown file."""

    with open(filename, encoding="utf-8") as file:
        lines = file.readlines()

    if not lines or lines[0].strip() != "---":
        return None

    yaml_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        yaml_lines.append(line)

    content = "".join(yaml_lines)
    return yaml.safe_load(content)


def read_from_markdown(filepath: str) -> dict[str, Any] | None:
    """Load and prepare metadata from a Markdown file."""

    metadata = get_frontmatter(filepath)
    if metadata is None:
        logger.debug("No frontmatter found in Markdown file", filename=filepath)
        return None

    from pie import build_index

    metadata["url"] = build_index.get_url(filepath)
    return metadata


def read_from_yaml(filepath: str) -> dict[str, Any] | None:
    """Load and validate metadata from a YAML file."""

    try:
        metadata = read_yaml(filepath)
        return fill_missing_metadata(metadata, filepath=filepath)
    except yaml.YAMLError:
        logger.warning("Failed to parse YAML file", filename=filepath)
        raise


def load_metadata_pair(path: Path) -> Mapping[str, Any] | None:
    """Load metadata from ``path`` and a sibling Markdown/YAML file.

    If both a ``.md`` and ``.yml``/``.yaml`` exist for the same base name,
    the metadata from each file is combined. Values from YAML override those
    from Markdown when keys conflict and a :class:`UserWarning` is emitted.
    Returns ``None`` if neither file contains metadata.

    Example
    -------
    >>> (tmp / 'post.md').write_text('---\nname: Post\n---\n')
    17
    >>> (tmp / 'post.yml').write_text('title: Example')
    17
    >>> load_metadata_pair(tmp / 'post.yml')
    {'name': 'Post', 'title': 'Example', 'id': 'post', 'path': ['post.yml', 'post.md']}
    """

    base = path.with_suffix("")
    md_path = base.with_suffix(".md")
    yml_path = base.with_suffix(".yml")
    yaml_path = base.with_suffix(".yaml")

    md_data = None
    if md_path.exists():
        md_data = read_from_markdown(str(md_path))

    yaml_data = None
    yaml_file: Path | None = None
    if yml_path.exists():
        yaml_file = yml_path
        yaml_data = read_from_yaml(str(yml_path))
    elif yaml_path.exists():
        yaml_file = yaml_path
        yaml_data = read_from_yaml(str(yaml_path))

    if md_data is None and yaml_data is None:
        return None

    combined: dict[str, Any] = {}
    if md_data:
        combined.update(md_data)
    if yaml_data:
        for k, v in yaml_data.items():
            if k in combined and combined[k] != v:
                warnings.warn(
                    f"Conflict for '{k}', using value from {yaml_file.name}",
                    UserWarning,
                )
            combined[k] = v

    files: list[Path] = []
    if yaml_file:
        files.append(yaml_file)
    if md_path.exists():
        files.append(md_path)

    fill_missing_metadata(combined, filepath=str(path))

    if files:
        combined["path"] = [str(p.resolve().relative_to(Path.cwd())) for p in files]

    logger.debug(combined)
    return combined


