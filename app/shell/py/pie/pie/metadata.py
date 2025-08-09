#!/usr/bin/env python3
"""Helpers for loading and retrieving document metadata."""

from __future__ import annotations

import json
import os
import warnings
from pathlib import Path
from typing import Any, Mapping

import redis
from flatten_dict import unflatten

from pie import build_index
from pie.logging import logger

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
        md_data = build_index.process_markdown(str(md_path))

    yaml_data = None
    yaml_file: Path | None = None
    if yml_path.exists():
        yaml_file = yml_path
        yaml_data = build_index.parse_yaml_metadata(str(yml_path))
    elif yaml_path.exists():
        yaml_file = yaml_path
        yaml_data = build_index.parse_yaml_metadata(str(yaml_path))

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

    if "id" not in combined:
        base = path.with_suffix("")
        combined["id"] = base.name
        logger.debug(
            "Generated 'id'",
            filename=str(path.resolve().relative_to(Path.cwd())),
            id=combined["id"],
        )

    if files:
        combined["path"] = [str(p.resolve().relative_to(Path.cwd())) for p in files]

    logger.debug(combined)
    return combined


