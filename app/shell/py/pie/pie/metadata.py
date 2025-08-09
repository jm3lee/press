#!/usr/bin/env python3
"""Helpers for retrieving metadata from Redis by file path."""

from __future__ import annotations

import os
from typing import Any

import redis

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
