from __future__ import annotations

import warnings
from pathlib import Path
from typing import Iterator, Mapping, Any, Tuple, Callable

from pie.metadata import get_metadata_by_path
from pie import metadata
from pie.logging import logger


def getopt_link(meta: Mapping[str, Any]) -> bool:
    """Return whether the item should be linked."""
    section = meta.get("indextree") or {}
    return section.get("link", True)


def getopt_show(meta: Mapping[str, Any]) -> bool:
    """Return whether the item should be shown."""
    section = meta.get("indextree") or {}
    return section.get("show", True)


def load_from_redis(path: Path) -> Mapping[str, Any] | None:
    """Fetch metadata for *path* from Redis."""

    filepath = str(path)
    doc_id = get_metadata_by_path(filepath, "id")
    if not doc_id:
        logger.debug("No doc_id found", path=filepath)
        return None

    meta = metadata.build_from_redis(f"{doc_id}.") or {}
    if "id" not in meta:
        meta["id"] = doc_id
    logger.debug("Fetched metadata via build_from_redis", path=filepath, id=doc_id)
    return meta


def walk(
    directory: Path,
    loader: Callable[[Path], Mapping[str, Any] | None] = load_from_redis,
) -> Iterator[Tuple[Mapping[str, Any], Path]]:
    """Yield metadata and path pairs for entries in *directory*."""
    for path in directory.iterdir():
        try:
            if path.is_dir():
                index_file = path / "index.yml"
                if index_file.is_file():
                    meta = loader(index_file)
                    if meta:
                        yield meta, path
            elif path.is_file() and path.suffix == ".yml" and path.name != "index.yml":
                meta = loader(path)
                if meta:
                    yield meta, path
        except Exception:
            warnings.warn(f"Failed to process {path}")
            raise


def sort_entries(entries: list[tuple[Mapping[str, Any], Path]]) -> None:
    """Sort *entries* in place for predictable index ordering.

    Entries are ordered by the following precedence:

    1. ``indextree.order`` metadata, if present
    2. Numerical filename or directory name
    3. Case-insensitive title
    """

    def sort_key(item: tuple[Mapping[str, Any], Path]) -> tuple[int, int | str]:
        """Return a ``(priority, value)`` tuple used for ordering.

        ``priority`` indicates which field determined the ordering:

        - ``0`` for explicit ``indextree.order``
        - ``1`` for a numeric filename or directory name
        - ``2`` for alphabetical title fallback

        ``value`` holds the associated sort value for comparison.
        """

        meta, path = item
        section = meta.get("indextree") or {}
        order = section.get("order")
        if order is not None:
            return (0, int(order))
        name = path.stem if path.is_file() else path.name
        if name.isdigit():
            return (1, int(name))
        return (2, meta["title"].lower())

    entries.sort(key=sort_key)
