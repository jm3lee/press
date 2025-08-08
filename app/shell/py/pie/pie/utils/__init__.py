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

import yaml

from pie.logging import logger


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


def read_yaml(filename: str):
    """Return YAML-decoded data from *filename*."""

    logger.debug("Reading YAML", filename=filename)
    with open(filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(data, filename: str) -> None:
    """Write *data* as YAML to *filename*."""

    logger.debug("Writing YAML", filename=filename)
    with open(filename, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def get_pubdate(date: datetime | None = None) -> str:
    """Return *date* formatted as ``Mon DD, YYYY``.

    If *date* is ``None`` the current date is used. This helper centralises the
    pubdate formatting used throughout the ``pie`` tools.
    """

    if date is None:
        date = datetime.now()
    return date.strftime("%b %d, %Y")
