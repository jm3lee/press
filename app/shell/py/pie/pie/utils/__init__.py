"""Utility helpers used throughout the ``pie`` package.

This module exposes a pre-configured :class:`loguru.logger` instance and a few
convenience functions for reading and writing UTF-8 encoded files.  The logger
defaults to writing INFO level messages to standard error but can be disabled or
directed to additional files if required.
"""

from __future__ import annotations

import argparse
import json
import sys

import yaml
from loguru import logger

# Remove default handlers provided by :mod:`loguru` so we can configure logging
# behaviour explicitly.
logger.remove()

LOG_FORMAT = (
    "{time:HH:mm:ss} {module:>25}:{function:<25}:{line:<4} {level:.4s} {message} {extra}"
)

# Configure the console sink that all tests and scripts rely on.
logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")


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


def disable_logging() -> None:
    """Disable all logging output for the :mod:`pie` helpers."""

    logger.remove()


def add_file_logger(filename: str, level: str = "DEBUG") -> None:
    """Add a log sink that writes to *filename* at the given *level*."""

    logger.add(filename, format=LOG_FORMAT, level=level)


def add_log_argument(parser: argparse.ArgumentParser, *, default: str | None = None) -> None:
    """Add a standard ``--log`` argument to *parser*.

    Parameters
    ----------
    parser:
        ``argparse`` parser to which the argument should be added.
    default:
        Optional default path for the log file.
    """

    parser.add_argument("-l", "--log", default=default, help="Write logs to the specified file")


def setup_file_logger(log_path: str | None, *, level: str = "DEBUG") -> None:
    """Configure file logging when ``log_path`` is provided."""

    if log_path:
        add_file_logger(log_path, level=level)
