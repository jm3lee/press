"""Centralised logging helpers for the :mod:`pie` package.

This module configures a :class:`loguru.logger` instance for use across the
project and provides small helper functions for integrating logging with
command line interfaces.
"""

from __future__ import annotations

import argparse
import sys
from loguru import logger

# Remove default handlers provided by :mod:`loguru` so we can configure logging
# behaviour explicitly.
logger.remove()

LOG_FORMAT = (
    "{time:HH:mm:ss} {module:>25}:{function:<25}:{line:<4} {level:.4s} {message} {extra}"
)

# Configure the console sink that all tests and scripts rely on.
logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")


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
