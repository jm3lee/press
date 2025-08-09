from __future__ import annotations

import argparse
import sys

import emoji
from pie.logging import logger, add_log_argument, setup_file_logger

def emojify_text(text: str) -> str:
    """Return *text* with ``:emoji:`` codes replaced by Unicode characters."""
    return emoji.emojize(text, language="alias")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Replace :emoji: codes with Unicode characters",
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="Text to emojify. Reads from stdin when omitted.",
    )
    add_log_argument(parser)
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: list[str] | None = None) -> None:
    """Entry point used by the ``emojify`` console script."""
    args = parse_args(argv)
    setup_file_logger(args.log)

    if args.text:
        text = " ".join(args.text)
        logger.debug("emojifying text", text=text)
        print(emojify_text(text))
    else:
        data = sys.stdin.read()
        logger.debug("emojifying stdin", length=len(data))
        if data:
            print(emojify_text(data), end="")


if __name__ == "__main__":  # pragma: no cover - convenience
    main()

