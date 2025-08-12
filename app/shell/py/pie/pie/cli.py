from __future__ import annotations

import argparse

from pie.logging import add_log_argument

__all__ = ["create_parser"]


def create_parser(description: str, *, log_default: str | None = None) -> argparse.ArgumentParser:
    """Return an :class:`argparse.ArgumentParser` with standard options.

    The parser includes ``--log`` and ``--verbose`` arguments used throughout
    the ``pie`` command line tools.

    Parameters
    ----------
    description:
        Description for the parser.
    log_default:
        Optional default path for the ``--log`` argument.
    """

    parser = argparse.ArgumentParser(description=description)
    add_log_argument(parser, default=log_default)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser
