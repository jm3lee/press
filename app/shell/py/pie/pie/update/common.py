"""Shared helpers for metadata update scripts.

These utilities power :mod:`pie.update.author` and :mod:`pie.update.pubdate` by
providing common routines for discovering changed files, modifying metadata, and
configuring log output.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Iterable

from pie.metadata import load_metadata_pair
from pie.logging import logger
import os

__all__ = [
    "get_changed_files",
    "replace_field",
    "update_files",
]


def get_changed_files() -> list[Path]:
    """Return paths of tracked files changed in git. Skip submodules by checking
    for directories."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as err:
        logger.warning("git executable not found", error=str(err))
        return []
    except subprocess.CalledProcessError as err:
        logger.warning("git repository not initialised", error=str(err))
        return []
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if not line or line.startswith("??"):
            continue
        parts = line.split()
        if os.path.isdir(parts[1]):
            continue
        if len(parts) >= 2:
            paths.append(Path(parts[-1]))
    return paths


def replace_field(fp: Path, field: str, value: str) -> tuple[bool, str | None]:
    """Replace ``field`` in *fp* and return (changed, old_value)."""
    text = fp.read_text(encoding="utf-8")
    if fp.suffix in {".yml", ".yaml"}:
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.startswith(f"{field}:"):
                old = line.split(":", 1)[1].strip()
                if old != value:
                    lines[i] = f"{field}: {value}\n"
                    fp.write_text("".join(lines), encoding="utf-8")
                    return True, old
                else:
                    return True, None
        lines.append(f"{field}: {value}\n")
        fp.write_text("".join(lines), encoding="utf-8")
        return True, "undefined"

    if fp.suffix == ".md":
        lines = text.splitlines(keepends=True)
        if not lines or not lines[0].startswith("---"):
            return False, None
        end = None
        for i in range(1, len(lines)):
            if lines[i].startswith("---"):
                end = i
                break
        if end is None:
            return False, None
        for i in range(1, end):
            if lines[i].startswith(f"{field}:"):
                old = lines[i].split(":", 1)[1].strip()
                lines[i] = f"{field}: {value}\n"
                fp.write_text("".join(lines), encoding="utf-8")
                return True, old
        return False, None

    return False, None


def update_files(paths: Iterable[Path], field: str, value: str) -> tuple[list[str], int]:
    """Update ``field`` in files related to *paths*.

    Returns a tuple ``(messages, checked)`` where ``messages`` contains log
    entries for each modified file and ``checked`` is the number of files that
    were examined.
    """
    changes: list[str] = []
    processed: set[Path] = set()
    checked = 0
    for path in paths:
        base = path.with_suffix("")
        if base in processed:
            continue
        processed.add(base)

        metadata = load_metadata_pair(path)
        file_paths: set[Path] = {path}
        if metadata and "path" in metadata:
            file_paths.update(Path(p) for p in metadata["path"])

        for fp in file_paths:
            if not fp.exists():
                continue
            checked += 1
            changed, old = replace_field(fp, field, value)
            if changed and old is not None:
                msg = f"{fp}: {old} -> {value}"
                logger.info(msg)
                changes.append(msg)
    return changes, checked


