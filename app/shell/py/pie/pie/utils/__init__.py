"""Utility helpers used throughout the ``pie`` package.

This module provides convenience functions for reading and writing UTF-8
encoded files as well as helper routines such as :func:`get_pubdate`. Logging
behaviour is centralised in :mod:`pie.logging` and the pre-configured
``loguru`` logger from that module is re-exported here for backwards
compatibility.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

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


def load_exclude_file(filename: str | Path | None, root: Path) -> set[Path]:
    """Return a set of resolved paths listed in *filename*.

    The YAML file may contain absolute paths or ones relative to *root*.
    If *filename* is ``None`` an empty set is returned.
    """

    exclude: set[Path] = set()
    if not filename:
        return exclude
    data = read_yaml(str(filename)) or []
    for item in data:
        p = Path(item)
        if not p.is_absolute():
            p = root / p
        exclude.add(p.resolve())
    return exclude


def get_pubdate(date: datetime | None = None) -> str:
    """Return *date* formatted as ``Mon DD, YYYY``.

    If *date* is ``None`` the current date is used. This helper centralises the
    pubdate formatting used throughout the ``pie`` tools.
    """

    if date is None:
        date = datetime.now()
    return date.strftime("%b %d, %Y")
