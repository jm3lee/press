#!/usr/bin/env python3
"""Load an index JSON file and insert values into DragonflyDB/Redis.

This command reads a JSON index mapping document ``id`` to metadata and
inserts each value into a Redis compatible database using keys of the form
``<id>.<property>``. Complex values are stored as JSON strings.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping
import warnings

import redis
from pie import build_index
from pie.utils import add_file_logger, logger


def load_index(path: str | Path) -> Mapping[str, Mapping[str, Any]]:
    """Return the parsed JSON index from *path*."""
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def flatten_index(index: Mapping[str, Mapping[str, Any]]) -> Iterable[tuple[str, str]]:
    """Yield ``(key, value)`` pairs for insertion into Redis.

    Nested dictionaries are flattened using dot-separated keys. Values that are
    not strings are encoded as JSON.
    """

    def _walk(prefix: str, obj: Any) -> Iterable[tuple[str, str]]:
        if isinstance(obj, Mapping):
            for k, v in obj.items():
                yield from _walk(f"{prefix}.{k}", v)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                yield from _walk(f"{prefix}.{i}", item)
        else:
            val = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
            yield prefix, val

    for doc_id, props in index.items():
        yield from _walk(doc_id, props)


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
        yaml_data = build_index.process_yaml(str(yml_path))
    elif yaml_path.exists():
        yaml_file = yaml_path
        yaml_data = build_index.process_yaml(str(yaml_path))

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

    if "id" not in combined:
        base = path.with_suffix('')
        combined["id"] = base.name
        logger.info("Generated 'id'", filename=str(path.resolve().relative_to(Path.cwd())), id=combined["id"])

    logger.info(combined)
    return combined


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Insert index values into a DragonflyDB/Redis instance",
    )
    parser.add_argument(
        "path",
        help="Path to index.json, a metadata file, or a directory containing YAML",
    )
    parser.add_argument("-l", "--log", help="Write logs to the specified file")
    parser.add_argument(
        "--host",
        default="localhost",
        help="Redis host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6379,
        help="Redis port (default: 6379)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def update_redis(conn: redis.Redis, index: Mapping[str, Mapping[str, Any]]) -> None:
    """Insert each value from *index* into *conn*."""
    for key, value in flatten_index(index):
        conn.set(key, value)
        logger.debug("Inserted", key=key, value=value)


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point for the ``update-index`` console script."""
    args = parse_args(argv)
    if args.log:
        add_file_logger(args.log, level="DEBUG")

    path = Path(args.path)
    r = redis.Redis(host=args.host, port=args.port, decode_responses=True)

    if path.is_dir():
        index: dict[str, dict[str, Any]] = {}
        for pattern in ("**/*.md", "**/*.yml", "**/*.yaml"):
            for p in path.glob(pattern):
                metadata = load_metadata_pair(p)
                if metadata:
                    index[metadata["id"]] = metadata
        update_redis(r, index)
        return

    if path.suffix.lower() == ".json":
        index = load_index(path)
        update_redis(r, index)
        return

    if path.suffix.lower() in {".md", ".yml", ".yaml"}:
        metadata = load_metadata_pair(path)
        if metadata is None:
            logger.error("No metadata found", filename=str(path))
            raise SystemExit(1)

        doc_id = metadata.get("id")
        if not doc_id:
            warnings.warn("Missing 'id' field in metadata", UserWarning)
            raise SystemExit(1)

        update_redis(r, {doc_id: metadata})
        return

    logger.error("Unsupported file type", filename=str(path))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
