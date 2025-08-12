from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, Sequence

from pie.logging import add_log_argument, configure_logging, logger

FILTERS = [
    "link",
    "linktitle",
    "linkcap",
    "linkshort",
    "linkicon",
    "link_icon_title",
]

PATTERNS = {
    name: re.compile(
        r"{{\s*(?P<val>[^{}]+?)\s*\|\s*" + name + r"\s*(?P<args>\([^{}]*\))?\s*}}"
    )
    for name in FILTERS
}


def replace_filters(text: str) -> tuple[str, int]:
    """Replace legacy link* filters with globals.

    Returns the modified text and the number of substitutions made.
    """

    total = 0

    def repl(name: str, match: re.Match[str]) -> str:
        nonlocal total
        val = match.group("val").strip()
        args = match.group("args")
        if args:
            inner = args[1:-1].strip()
            if inner:
                total += 1
                return f"{{{{ {name}({val}, {inner}) }}}}"
        total += 1
        return f"{{{{ {name}({val}) }}}}"

    for name, pattern in PATTERNS.items():
        text = pattern.sub(lambda m, n=name: repl(n, m), text)
    return text, total


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    """Yield files under *paths* recursively."""

    for p in paths:
        if p.is_file():
            yield p
        elif p.is_dir():
            for fp in p.rglob("*"):
                if fp.is_file():
                    yield fp


def process_file(path: Path) -> bool:
    """Convert link filters in *path*.

    Returns ``True`` if the file was modified.
    """

    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    new_text, count = replace_filters(text)
    if count:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Best-effort rewrite of legacy link* filters to globals",
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to rewrite")
    add_log_argument(parser, default="log/update-link-filters.txt")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    files = list(iter_files(Path(p) for p in args.paths))
    changed = 0
    for fp in files:
        if process_file(fp):
            changed += 1
            print(str(fp))
            logger.info("updated", file=str(fp))
    print(f"{len(files)} {'file' if len(files)==1 else 'files'} checked")
    print(f"{changed} {'file' if changed==1 else 'files'} changed")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
