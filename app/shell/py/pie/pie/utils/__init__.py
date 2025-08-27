"""Utility helpers used throughout the ``pie`` package.

This module provides convenience functions for reading and writing UTF-8
encoded files as well as helper routines such as :func:`get_pubdate`. Logging
behaviour is centralised in :mod:`pie.logging` and the pre-configured
``loguru`` logger from that module is re-exported here for backwards
compatibility.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable

from pie.logging import logger
from pie.yaml import read_yaml, write_yaml


def read_utf8(filename: str) -> str:
    """Return the contents of *filename* decoded as UTF-8."""

    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def read_json(filename: str):
    """Return JSON-decoded data from *filename*."""

    logger.debug("Reading JSON", filename=filename)
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(data, filename: str) -> None:
    """Write *data* as JSON to *filename*."""

    logger.debug("Writing JSON", filename=filename)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f)


def write_utf8(text: str, filename: str) -> None:
    """Write *text* to *filename* encoded as UTF-8."""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


class ExcludeList:
    """Collection of file patterns to skip when scanning directories.

    Items may be literal paths, shell-style wildcards, or regular
    expressions prefixed with ``regex:``.
    """

    def __init__(self, items: Iterable[str], root: Path) -> None:
        self.root = root
        self.paths: set[Path] = set()
        self.wildcards: list[str] = []
        self.regexes: list[re.Pattern[str]] = []
        for raw in items:
            if raw.startswith("regex:") or raw.startswith("re:"):
                pattern = raw.split(":", 1)[1]
                self.regexes.append(re.compile(pattern))
            elif any(ch in raw for ch in "*?[]"):
                p = Path(raw)
                if not p.is_absolute():
                    p = root / raw
                self.wildcards.append(p.as_posix())
            else:
                p = Path(raw)
                if not p.is_absolute():
                    p = root / p
                self.paths.add(p.resolve())

    def __contains__(self, path: Path) -> bool:
        p = path.resolve()
        if p in self.paths:
            return True
        abs_str = p.as_posix()
        try:
            rel_str = p.relative_to(self.root).as_posix()
        except ValueError:
            rel_str = None
        for pattern in self.wildcards:
            if fnmatch(abs_str, pattern):
                return True
            if rel_str and fnmatch(rel_str, pattern):
                return True
        for regex in self.regexes:
            if regex.search(abs_str):
                return True
            if rel_str and regex.search(rel_str):
                return True
        return False


def load_exclude_file(filename: str | Path | None, root: Path) -> ExcludeList:
    """Return an :class:`ExcludeList` from *filename*.

    The YAML file may contain absolute paths or ones relative to *root*.
    If *filename* is ``None`` an empty :class:`ExcludeList` is returned.
    """

    data: list[str] = []
    if filename:
        data = read_yaml(str(filename)) or []
    return ExcludeList(data, root)


def get_pubdate(date: datetime | None = None) -> str:
    """Return *date* formatted as ``Mon DD, YYYY``.

    If *date* is ``None`` the current date is used. This helper centralises the
    pubdate formatting used throughout the ``pie`` tools.
    """

    if date is None:
        date = datetime.now()
    return date.strftime("%b %d, %Y")
