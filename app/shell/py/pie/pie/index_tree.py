from __future__ import annotations

import warnings
from pathlib import Path
from typing import Iterator, Mapping, Any, Tuple, Callable

from pie.load_metadata import load_yaml_metadata


def getopt_link(meta: Mapping[str, Any]) -> bool:
    """Return whether the item should be linked."""
    section = meta.get("gen-markdown-index") or {}
    return section.get("link", True)


def getopt_show(meta: Mapping[str, Any]) -> bool:
    """Return whether the item should be shown."""
    section = meta.get("gen-markdown-index") or {}
    return section.get("show", True)


def walk(
    directory: Path,
    loader: Callable[[Path], Mapping[str, Any] | None] = load_yaml_metadata,
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
