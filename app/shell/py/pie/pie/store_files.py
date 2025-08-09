from __future__ import annotations

import argparse
import shutil
import string
import secrets
from pathlib import Path
from typing import Iterable, Sequence

from pie.logging import add_log_argument, setup_file_logger, logger
from pie.utils import write_yaml

__all__ = ["main"]


ALPHABET = string.ascii_letters + string.digits


def generate_id(size: int = 8) -> str:
    """Return a random identifier of *size* characters."""
    return "".join(secrets.choice(ALPHABET) for _ in range(size))


def iter_files(path: Path) -> Iterable[Path]:
    """Yield files under *path* recursively."""
    if path.is_dir():
        yield from (p for p in path.rglob("*") if p.is_file())
    elif path.is_file():
        yield path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Move files to s3/v2 and create metadata entries",
    )
    parser.add_argument("path", help="Path to file or directory to process")
    parser.add_argument(
        "-n",
        dest="limit",
        type=int,
        help="Limit number of files processed",
    )
    add_log_argument(parser)
    return parser.parse_args(list(argv) if argv is not None else None)


def process_file(src: Path, dest_dir: Path, meta_dir: Path) -> str:
    """Move *src* to *dest_dir* and create metadata in *meta_dir*.

    Returns the generated file identifier.
    """
    file_id = generate_id()
    dest_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / file_id
    shutil.move(str(src), dest_path)

    metadata = {
        "id": file_id,
        "author": "",
        "pubdate": "",
        "url": f"/v2/files/0/{file_id}",
    }
    meta_path = meta_dir / f"{file_id}.yml"
    write_yaml(metadata, str(meta_path))

    logger.info(
        "processed file",
        src=str(src),
        dest=str(dest_path),
        meta=str(meta_path),
    )
    return file_id


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``store-files`` console script."""
    args = parse_args(argv)
    if args.log:
        setup_file_logger(args.log, level="INFO")

    base_path = Path(args.path)
    dest_dir = Path("s3") / "v2" / "files" / "0"
    meta_dir = Path("src") / "static" / "files"

    count = 0
    for src in iter_files(base_path):
        process_file(src, dest_dir, meta_dir)
        count += 1
        if args.limit and count >= args.limit:
            break
    logger.info("completed", processed=count)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
