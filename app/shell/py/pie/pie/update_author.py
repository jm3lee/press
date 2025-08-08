from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
from typing import Iterable, Sequence

import yaml

from pie.load_metadata import load_metadata_pair
from pie.utils import add_file_logger, logger

__all__ = ["main"]


def load_default_author(cfg_path: Path | None = None) -> str:
    """Return the default author from ``cfg/update-author.yml``."""
    path = cfg_path or Path("cfg") / "update-author.yml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ""
    if isinstance(data, dict):
        return str(data.get("author", ""))
    if isinstance(data, str):
        return data
    return ""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    default_author = load_default_author()
    parser = argparse.ArgumentParser(
        description="Update the author field in modified metadata files",
    )
    parser.add_argument(
        "--author",
        default=default_author,
        help="Author name to set (default: value from cfg/update-author.yml)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def get_changed_files() -> list[Path]:
    """Return paths of files changed in git, excluding untracked files."""
    result = subprocess.run(
        ["git", "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    )
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if not line or line.startswith("??"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            paths.append(Path(parts[-1]))
    return paths


def _replace_author(fp: Path, author: str) -> tuple[bool, str | None]:
    """Replace ``author`` in *fp* and return (changed, old_value)."""
    text = fp.read_text(encoding="utf-8")
    if fp.suffix in {".yml", ".yaml"}:
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.startswith("author:"):
                old = line.split(":", 1)[1].strip()
                if old != author:
                    lines[i] = f"author: {author}\n"
                    fp.write_text("".join(lines), encoding="utf-8")
                    return True, old
                else:
                    return True, None
        lines.append(f"author: {author}\n")
        fp.write_text("".join(lines), encoding="utf-8")
        return True, "undefined"

    if fp.suffix == ".md":
        lines = text.splitlines(keepends=True)
        if not lines or not lines[0].startswith("---"):
            return False, None
        end = None
        for i in range(1, len(lines)):
            if lines[i].startswith("---"):
                end = i
                break
        if end is None:
            return False, None
        for i in range(1, end):
            if lines[i].startswith("author:"):
                old = lines[i].split(":", 1)[1].strip()
                lines[i] = f"author: {author}\n"
                fp.write_text("".join(lines), encoding="utf-8")
                return True, old
        return False, None

    return False, None


def update_files(paths: Iterable[Path], author: str) -> list[str]:
    """Update ``author`` in files related to *paths* and return messages."""
    changes: list[str] = []
    processed: set[Path] = set()
    for path in paths:
        base = path.with_suffix("")
        if base in processed:
            continue
        processed.add(base)

        metadata = load_metadata_pair(path)
        file_paths: set[Path] = {path}
        if metadata and "path" in metadata:
            file_paths.update(Path(p) for p in metadata["path"])

        for fp in file_paths:
            if not fp.exists():
                continue
            changed, old = _replace_author(fp, author)
            if changed and old is not None:
                msg = f"{fp}: {old} -> {author}"
                logger.info(msg)
                changes.append(msg)
    return changes


def configure_logging() -> None:
    """Configure logging to write to ``log/update-author.txt``."""
    log_file = Path("log") / "update-author.txt"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    add_file_logger(str(log_file), level="INFO")


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``update-author`` console script."""
    args = parse_args(argv)
    configure_logging()
    changed = get_changed_files()
    messages = update_files(changed, args.author)
    for msg in messages:
        print(msg)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())

