#!/usr/bin/env python3
"""Load an index JSON file and insert values into DragonflyDB/Redis.

This command reads a JSON index mapping document ``id`` to metadata and
inserts each value into a Redis compatible database using keys of the form
``<id>.<property>``. Complex values are stored as JSON strings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Iterable, Mapping

import redis
from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.metadata import load_metadata_pair

METADATA_EXTS = {".md", ".mdi", ".yml", ".yaml"}


def load_index(path: str | Path) -> Mapping[str, Mapping[str, Any]]:
    """Return the parsed JSON index from *path*."""
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def _flatten_mapping(prefix, obj):
    for k, v in obj.items():
        yield from _walk(f"{prefix}.{k}", v)


def _walk(prefix: str, obj: Any) -> Iterable[tuple[str, str]]:
    if isinstance(obj, Mapping):
        yield from _flatten_mapping(prefix, obj)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            yield from _walk(f"{prefix}.{i}", item)
    else:
        val = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
        yield prefix, val


def flatten_index(index: Mapping[str, Mapping[str, Any]]) -> Iterable[tuple[str, str]]:
    """Yield ``(key, value)`` pairs for insertion into Redis.

    Nested dictionaries are flattened using dot-separated keys. Values that
    are not strings are encoded as JSON. Paths are stored as a JSON array under
    ``<id>.path`` and SHA1 hashes of each source file are stored as a JSON
    object under ``<id>.sha1``.
    """

    for doc_id, props in index.items():
        yield from _walk(doc_id, props)
        paths = props.get("path")
        if isinstance(paths, list):
            sha1_map: dict[str, str] = {}
            for p in paths:
                try:
                    abs_path = Path(p).resolve()
                    rel_path = abs_path.relative_to(Path.cwd())
                    digest = hashlib.sha1(abs_path.read_bytes()).hexdigest()
                    sha1_map[str(rel_path)] = digest
                    yield str(rel_path), doc_id
                except FileNotFoundError:
                    logger.warning("Source file missing", path=p)
            if sha1_map:
                yield from _flatten_mapping(f"{doc_id}.sha1", sha1_map)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser("Insert index values into a DragonflyDB/Redis instance")
    parser.add_argument(
        "path",
        help="Path to index.json, a metadata file, or a directory containing YAML",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("REDIS_HOST", "dragonfly"),
        help="Redis host (default: env REDIS_HOST or 'dragonfly')",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("REDIS_PORT", "6379")),
        help="Redis port (default: env REDIS_PORT or 6379)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def update_redis(conn: redis.Redis, index: Mapping[str, Mapping[str, Any]]) -> None:
    """Insert each value from *index* into *conn* using pipelined writes."""
    with conn.pipeline(transaction=False) as pipe:
        for key, value in flatten_index(index):
            pipe.set(key, value)
            logger.debug("Inserted", key=key, value=value)
        pipe.execute()


def load_directory_index(path: Path) -> tuple[dict[str, dict[str, Any]], int]:
    """Return an index built from all metadata files under *path*.

    The directory is scanned for ``.md``, ``.yml``, and ``.yaml`` files. Each
    pair of files is loaded with :func:`load_metadata_pair` using a thread
    pool. The returned tuple contains the combined index and the number of
    files that were processed.
    """

    processed: set[Path] = set()
    paths: list[Path] = []

    for root, _, files in os.walk(path):
        root_path = Path(root)
        for name in files:
            p = root_path / name
            if p.suffix.lower() not in METADATA_EXTS:
                continue
            base = p.with_suffix("")
            if base in processed:
                continue
            processed.add(base)
            paths.append(p)

    index: dict[str, dict[str, Any]] = {}
    num_workers = min(10, max(2, os.cpu_count() or 1))
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for metadata in executor.map(load_metadata_pair, paths):
            if metadata:
                index[metadata["id"]] = metadata

    return index, len(paths)


def load_index_from_path(path: Path) -> tuple[dict[str, dict[str, Any]], int]:
    """Load an index from *path* and return it with the number of files read."""

    if path.is_dir():
        return load_directory_index(path)

    if path.suffix.lower() == ".json":
        return load_index(path), 1

    if path.suffix.lower() in METADATA_EXTS:
        metadata = load_metadata_pair(path)
        if metadata is None:
            logger.error("No metadata found", filename=str(path))
            raise SystemExit(1)

        doc_id = metadata.get("id")
        if not doc_id:
            warnings.warn("Missing 'id' field in metadata", UserWarning)
            raise SystemExit(1)

        return {doc_id: metadata}, 1

    logger.error("Unsupported file type", filename=str(path))
    raise SystemExit(1)


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point for the ``update-index`` console script."""
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)

    start = time.perf_counter()
    path = Path(args.path)
    logger.debug("Connecting to Redis", host=args.host, port=args.port)
    r = redis.Redis(host=args.host, port=args.port, decode_responses=True)

    index, files_scanned = load_index_from_path(path)
    logger.debug("Loaded index", entries=len(index))
    update_redis(r, index)

    elapsed = time.perf_counter() - start
    logger.info("update complete", files=files_scanned, elapsed=f"{elapsed:.2f}s")


if __name__ == "__main__":
    main()
