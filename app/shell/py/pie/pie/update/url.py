from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from .common import get_changed_files, update_files as common_update_files
from pie.metadata import load_metadata_pair

__all__ = ["main"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Replace underscores with dashes in filenames and metadata url fields",
        log_default="log/update-url.txt",
    )
    parser.add_argument(
        "--sort-keys",
        action="store_true",
        help="Sort keys when writing YAML output",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def update_files(paths: Iterable[Path], sort_keys: bool = False) -> tuple[list[str], int]:
    """Rename files and update url fields for all *paths*.

    Returns a tuple ``(messages, checked)`` where ``messages`` contains log
    entries for each modification and ``checked`` is the number of files that
    were examined. When ``sort_keys`` is true YAML mappings are serialized with
    keys in sorted order.
    """
    messages: list[str] = []
    processed: set[Path] = set()
    checked = 0

    for path in paths:
        base = path.with_suffix("")
        if base in processed:
            continue
        processed.add(base)

        metadata = load_metadata_pair(path)
        file_paths: set[Path] = {path}
        if metadata and "path" in metadata:
            file_paths.update(Path(p) for p in metadata["path"])

        renamed_paths: list[Path] = []
        for fp in sorted(file_paths):
            if not fp.exists():
                continue
            checked += 1
            new_fp = fp.with_name(fp.name.replace("_", "-"))
            if new_fp != fp:
                fp.rename(new_fp)
                msg = f"{fp} -> {new_fp}"
                logger.info(msg)
                messages.append(msg)
            renamed_paths.append(new_fp)

        if metadata and isinstance(metadata.get("url"), str):
            old_url = metadata["url"]
            new_url = old_url.replace("_", "-")
            if new_url != old_url:
                url_msgs, _ = common_update_files(
                    renamed_paths, "url", new_url, sort_keys=sort_keys
                )
                messages.extend(url_msgs)

    return messages, checked


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``update-url`` console script."""
    args = parse_args(argv)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)
    changed = get_changed_files()
    changed = list(filter(lambda p: str(p).startswith("src/"), changed))
    messages, checked = update_files(changed, args.sort_keys)
    changed_count = len(messages)
    logger.info("Summary", checked=checked, changed_count=changed_count)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
