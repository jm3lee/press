from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.metadata import load_metadata_pair
from .common import collect_paths, get_changed_files

__all__ = ["main"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser(
        "Merge YAML data into metadata files",
        log_default="log/update-metadata.txt",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        help="YAML file containing fields to add",
    )
    parser.add_argument(
        "--sort-keys",
        action="store_true",
        help="Sort keys when writing YAML output",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help=(
            "Directories, files, or glob patterns to scan; if omitted, changed files"
            " are read from git"
        ),
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _merge(a: Any, b: Any) -> tuple[Any | None, bool]:
    """Recursively merge ``b`` into ``a``.

    Returns a tuple ``(result, conflict)`` where ``conflict`` is true when the
    merge could not be completed.
    """
    if isinstance(a, dict) and isinstance(b, dict):
        result: dict[str, Any] = dict(a)
        for key, value in b.items():
            if key in result:
                merged, conflict = _merge(result[key], value)
                if conflict:
                    return None, True
                result[key] = merged
            else:
                result[key] = value
        return result, False
    if isinstance(a, list) and isinstance(b, list):
        result_list = list(a)
        for item in b:
            if item not in result_list:
                result_list.append(item)
        return result_list, False
    if a is None:
        return b, False
    if a == b:
        return a, False
    return None, True


def _merge_file(fp: Path, data: dict, sort_keys: bool) -> tuple[bool, bool]:
    """Merge ``data`` into metadata of ``fp``.

    Returns ``(changed, conflict)``.
    """
    text = fp.read_text(encoding="utf-8") if fp.exists() else ""
    if fp.suffix in {".yml", ".yaml"}:
        existing = yaml.safe_load(text) or {}
        merged, conflict = _merge(existing, data)
        if conflict:
            return False, True
        if merged != existing:
            fp.write_text(
                yaml.safe_dump(merged, sort_keys=sort_keys), encoding="utf-8"
            )
            return True, False
        return False, False
    if fp.suffix == ".md":
        lines = text.splitlines(keepends=True)
        if lines and lines[0].startswith("---"):
            end = None
            for i in range(1, len(lines)):
                if lines[i].startswith("---"):
                    end = i
                    break
            if end is None:
                return False, True
            frontmatter = "".join(lines[1:end])
            existing = yaml.safe_load(frontmatter) or {}
            merged, conflict = _merge(existing, data)
            if conflict:
                return False, True
            if merged != existing:
                dumped = yaml.safe_dump(merged, sort_keys=sort_keys)
                lines[1:end] = [dumped]
                fp.write_text("".join(lines), encoding="utf-8")
                return True, False
            return False, False
        else:
            merged, conflict = _merge({}, data)
            if conflict:
                return False, True
            dumped = yaml.safe_dump(merged, sort_keys=sort_keys)
            new_lines = ["---\n", dumped, "---\n"] + lines
            fp.write_text("".join(new_lines), encoding="utf-8")
            return True, False
    return False, False

def _read_data(path: Path | None) -> dict:
    """Load YAML mapping from *path* or stdin."""
    if path:
        text = path.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        logger.warning("Input YAML must define a mapping")
        raise SystemExit(1)
    return data

def update_files(paths: Iterable[Path], data: dict, sort_keys: bool) -> tuple[list[str], int, bool]:
    """Update metadata for *paths* by merging ``data``.

    Returns ``(messages, checked, conflict)`` where ``conflict`` is true if any
    file could not be merged.
    """
    messages: list[str] = []
    processed: set[Path] = set()
    checked = 0
    conflict_found = False

    for path in paths:
        base = path.with_suffix("")
        if base in processed:
            continue
        processed.add(base)

        metadata = load_metadata_pair(path)
        file_paths: set[Path] = {path}
        if metadata and "path" in metadata:
            file_paths.update(Path(p) for p in metadata["path"])

        yaml_files = [fp for fp in file_paths if fp.suffix in {".yml", ".yaml"}]
        target_files = yaml_files or sorted(file_paths)

        for fp in target_files:
            if not fp.exists():
                continue
            checked += 1
            changed, conflict = _merge_file(fp, data, sort_keys)
            if conflict:
                logger.warning("Conflict merging metadata for {}", fp)
                conflict_found = True
                continue
            if changed:
                msg = f"{fp} updated"
                logger.info(msg)
                messages.append(msg)
    return messages, checked, conflict_found

def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``update-metadata`` console script."""
    args = parse_args(argv)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)
    logger.debug("Parsed arguments", args=vars(args))
    data = _read_data(args.file)
    logger.debug("Data to merge", data=data)
    if args.paths:
        changed = collect_paths(args.paths)
    else:
        changed = get_changed_files()
    logger.debug("Files to update", files=[str(p) for p in changed])
    messages, checked, conflict = update_files(changed, data, args.sort_keys)
    logger.debug("Update complete", messages=messages, checked=checked, conflict=conflict)
    logger.info("Summary", checked=checked, changed_count=len(messages))
    return 1 if conflict else 0

if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
