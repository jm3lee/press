#!/usr/bin/env python3
"""Helpers for loading and retrieving document metadata."""

from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Any, Mapping

import redis

from pie import build_index
from pie.logging import logger
from pie.utils import read_yaml

redis_conn: redis.Redis | None = None


def get_metadata_by_path(filepath: str, keypath: str) -> Any | None:
    """Return metadata value for ``keypath`` associated with ``filepath``.

    The function first looks up the document ``id`` stored under ``filepath``
    in Redis and then retrieves ``<id>.<keypath>``.
    """

    global redis_conn
    if redis_conn is None:
        host = os.getenv("REDIS_HOST", "dragonfly")
        port = int(os.getenv("REDIS_PORT", "6379"))
        redis_conn = redis.Redis(host=host, port=port, decode_responses=True)

    doc_id = redis_conn.get(filepath)
    if not doc_id:
        return None
    return redis_conn.get(f"{doc_id}.{keypath}")


def load_metadata_pair(path: Path) -> Mapping[str, Any] | None:
    """Load metadata from ``path`` and a sibling Markdown/YAML file.

    If both a ``.md`` and ``.yml``/``.yaml`` exist for the same base name,
    the metadata from each file is combined. Values from YAML override those
    from Markdown when keys conflict and a :class:`UserWarning` is emitted.
    Returns ``None`` if neither file contains metadata.
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


def load_yaml_metadata(path: Path) -> Mapping[str, Any] | None:
    """Return metadata loaded from a YAML file.

    Missing fields like ``id`` and ``url`` are generated when possible to
    provide a consistent shape with :func:`load_metadata_pair`.
    """

    try:
        data = read_yaml(str(path)) or {}
    except Exception as exc:  # pragma: no cover - warning path
        warnings.warn(f"Invalid YAML: {path} ({exc})")
        return None

    if "id" not in data:
        data["id"] = path.with_suffix("").name

    if "url" not in data:
        try:
            data["url"] = build_index.get_url(str(path))
        except Exception:
            pass

    return data
