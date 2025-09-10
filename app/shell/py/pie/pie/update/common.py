"""Shared helpers for metadata update scripts.

These utilities power :mod:`pie.update.author` and :mod:`pie.update.pubdate` by
providing common routines for discovering changed files, modifying metadata, and
configuring log output.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import glob
from itertools import chain
from typing import Iterable

from pie.metadata import load_metadata_pair
from pie.logging import logger
import os
from io import StringIO
from pie.yaml import YAML_EXTS, yaml, write_yaml

__all__ = [
    "get_changed_files",
    "replace_field",
    "update_files",
    "collect_paths",
]


def get_changed_files() -> list[Path]:
    """Return paths of tracked files changed in git. Skip submodules by checking
    for directories."""
    try:
        result = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={Path.cwd()}",
                "status",
                "--short",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as err:
        logger.warning("git executable not found", error=str(err))
        return []
    except subprocess.CalledProcessError as err:
        stderr = (err.stderr or "").lower()
        if "dubious ownership" in stderr or "safe.directory" in stderr:
            logger.warning(
                f"run: git config --global --add safe.directory {Path.cwd()}",
                error=str(err),
            )
        else:
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


def collect_paths(patterns: Iterable[str]) -> list[Path]:
    """Expand *patterns* into Markdown and YAML files.

    Each pattern may refer to a file, directory, or glob. Returned paths are
    relative to the current working directory. Non-existent paths are skipped
    and duplicates are removed while preserving order.
    """
    cwd = Path.cwd()
    seen: set[Path] = set()
    results: list[Path] = []
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True) or [pattern]
        for match in matches:
            p = Path(match)
            if not p.exists():
                continue
            if p.is_dir():
                for child in chain(
                    p.rglob("*.md"),
                    *(p.rglob(f"*{ext}") for ext in YAML_EXTS),
                ):
                    if child.is_file():
                        rel = child.relative_to(cwd) if child.is_absolute() else child
                        if rel not in seen:
                            seen.add(rel)
                            results.append(rel)
            else:
                if p.suffix in {".md"} | YAML_EXTS:
                    rel = p.relative_to(cwd) if p.is_absolute() else p
                    if rel not in seen:
                        seen.add(rel)
                        results.append(rel)
    return results


def replace_field(
    fp: Path, field: str, value: str, sort_keys: bool = False
) -> tuple[bool, str | None]:
    """Replace ``field`` in *fp* and return ``(changed, old_value)``.

    ``field`` may reference nested mappings using dot notation, for example
    ``doc.author``.

    When ``sort_keys`` is true YAML mappings are written with keys in sorted
    order.
    """
    text = fp.read_text(encoding="utf-8")
    if fp.suffix in YAML_EXTS:
        return _replace_yaml_field(fp, text, field, value, sort_keys)
    if fp.suffix == ".md":
        return _replace_markdown_field(fp, text, field, value, sort_keys)
    return False, None


def _replace_yaml_field(
    fp: Path, text: str, field: str, value: str, sort_keys: bool
) -> tuple[bool, str | None]:
    """Update ``field`` in YAML *fp*, optionally sorting keys."""
    data = yaml.load(text) or {}
    changed, old = _set_nested(data, field.split("."), value)
    if changed:
        yaml.sort_keys = sort_keys
        write_yaml(data, fp)
        return True, old
    return True, None


def _replace_markdown_field(
    fp: Path, text: str, field: str, value: str, sort_keys: bool
) -> tuple[bool, str | None]:
    """Update ``field`` in Markdown frontmatter of *fp*.

    When ``sort_keys`` is true the frontmatter mapping is written with keys in
    sorted order.
    """
    lines = text.splitlines(keepends=True)
    keys = field.split(".")
    if not lines or not lines[0].startswith("---"):
        # no frontmatter, add a new block with the field
        buf = StringIO()
        data: dict[str, object] = {}
        _set_nested(data, keys, value)
        yaml.sort_keys = sort_keys
        yaml.dump(data, buf)
        dumped = buf.getvalue()
        new_lines = ["---\n", dumped, "---\n"] + lines
        fp.write_text("".join(new_lines), encoding="utf-8")
        return True, "undefined"
    end = None
    for i in range(1, len(lines)):
        if lines[i].startswith("---"):
            end = i
            break
    if end is None:
        return False, None
    frontmatter = "".join(lines[1:end])
    data = yaml.load(frontmatter) or {}
    changed, old = _set_nested(data, keys, value)
    if changed:
        buf = StringIO()
        yaml.sort_keys = sort_keys
        yaml.dump(data, buf)
        dumped = buf.getvalue()
        lines[1:end] = [dumped]
        fp.write_text("".join(lines), encoding="utf-8")
        return True, old
    return True, None


def _set_nested(data: dict, keys: list[str], value: str) -> tuple[bool, str | None]:
    """Set ``value`` at ``keys`` within ``data``.

    Returns ``(changed, old_value)`` where ``old_value`` is ``"undefined"`` when
    no prior value existed.
    """
    cur = data
    for key in keys[:-1]:
        child = cur.get(key)
        if not isinstance(child, dict):
            child = {}
            cur[key] = child
        cur = child
    old = cur.get(keys[-1])
    if old != value:
        cur[keys[-1]] = value
        return True, old if old is not None else "undefined"
    return False, None




def update_files(
    paths: Iterable[Path], field: str, value: str, sort_keys: bool = False
) -> tuple[list[str], int]:
    """Update ``field`` in files related to *paths*.

    Returns a tuple ``(messages, checked)`` where ``messages`` contains log
    entries for each modified file and ``checked`` is the number of files that
    were examined. When ``sort_keys`` is true YAML mappings are serialized with
    keys in sorted order.
    """
    changes: list[str] = []
    processed: set[Path] = set()
    checked = 0
    logger.debug("", paths=paths, field=field, value=value, sort_keys=sort_keys)
    for path in paths:
        base = path.with_suffix("")
        if base in processed:
            continue
        processed.add(base)

        metadata = load_metadata_pair(path)
        file_paths: set[Path] = {path}
        if metadata and "path" in metadata:
            file_paths.update(Path(p) for p in metadata["path"])

        yaml_files = sorted([fp for fp in file_paths if fp.suffix in YAML_EXTS])
        target_files = yaml_files or sorted(file_paths)
        logger.debug("", target_files=target_files)

        for fp in target_files:
            if not fp.exists():
                continue
            checked += 1
            changed, old = replace_field(fp, field, value, sort_keys)
            if changed and old is not None:
                msg = f"{fp}: {old} -> {value}"
                logger.info(msg)
                changes.append(msg)
    return changes, checked


