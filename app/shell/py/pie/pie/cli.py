from __future__ import annotations

import argparse

from pie.logging import add_log_argument

__all__ = ["create_parser"]


def create_parser(
    description: str,
    *,
    log_default: str | None = None,
    warnings: bool = False,
) -> argparse.ArgumentParser:
    """Return an :class:`argparse.ArgumentParser` with standard options.

    The parser includes ``--log`` and ``--verbose`` arguments used throughout
    the ``pie`` command line tools.

    Parameters
    ----------
    description:
        Description for the parser.
    log_default:
        Optional default path for the ``--log`` argument.
    warnings:
        When :data:`True`, add a ``-w/--warn`` flag that treats errors as
        warnings and forces a successful exit code.
    """

    parser = argparse.ArgumentParser(description=description)
    add_log_argument(parser, default=log_default)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    if warnings:
        parser.add_argument(
            "-w",
            "--warn",
            action="store_true",
            help="Treat errors as warnings and exit with success",
        )
    return parser
