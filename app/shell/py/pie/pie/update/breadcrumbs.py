"""Update ``doc.breadcrumbs`` entries to match file paths."""

from __future__ import annotations

import argparse
from io import StringIO
from pathlib import Path
from typing import Iterable, Sequence

from pie.cli import create_parser
from pie.logging import configure_logging, logger
from pie.metadata import load_metadata_pair
from pie.yaml import YAML_EXTS, yaml, write_yaml

DEFAULT_LOG = "log/update-breadcrumbs.txt"

__all__ = ["main"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

    parser = create_parser(
        "Update doc.breadcrumbs arrays based on file locations",
        log_default=DEFAULT_LOG,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="src",
        help="Directory to scan for metadata files",
    )
    parser.add_argument(
        "--sort-keys",
        action="store_true",
        help="Sort keys when writing YAML output",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _title_from_slug(slug: str) -> str:
    """Return a human readable title from *slug*."""

    return slug.replace("-", " ").replace("_", " ").title()


def _iter_metadata_files(root: Path) -> Iterable[tuple[Path, Path, dict | None]]:
    """Yield ``(base, path, metadata)`` for files discovered under *root*."""

    processed: set[Path] = set()
    patterns = ("*.md", "*.mdi", "*.yml", "*.yaml")
    for pattern in patterns:
        for path in root.rglob(pattern):
            if not path.is_file():
                continue
            base = path.with_suffix("")
            if base in processed:
                continue
            processed.add(base)
            yield base, path, load_metadata_pair(path)


def _normalise_breadcrumbs(data: object) -> list[dict[str, str]]:
    """Return breadcrumb entries containing only ``title``/``url`` keys."""

    results: list[dict[str, str]] = []
    if not isinstance(data, list):
        return results
    for item in data:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        if not isinstance(title, str):
            continue
        crumb: dict[str, str] = {"title": title}
        url = item.get("url")
        if isinstance(url, str) and url:
            crumb["url"] = url
        results.append(crumb)
    return results


def _expected_breadcrumbs(
    base: Path, root: Path, existing: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Return breadcrumb trail for ``base`` relative to ``root``."""

    try:
        parts = list(base.relative_to(root).parts)
    except ValueError:
        parts = list(base.parts)

    breadcrumbs: list[dict[str, str]] = [{"title": "Home", "url": "/"}]
    for index, part in enumerate(parts, start=1):
        title = existing[index]["title"] if index < len(existing) else None
        if not title:
            title = _title_from_slug(part)
        if index < len(parts):
            url = "/" + "/".join(parts[:index]) + "/"
            breadcrumbs.append({"title": title, "url": url})
        else:
            breadcrumbs.append({"title": title})
    return breadcrumbs


def _write_yaml_breadcrumbs(
    fp: Path, breadcrumbs: list[dict[str, str]], sort_keys: bool
) -> bool:
    """Update ``doc.breadcrumbs`` in YAML file *fp* if needed."""

    text = fp.read_text(encoding="utf-8") if fp.exists() else ""
    data = yaml.load(text) or {}
    doc = data.setdefault("doc", {})
    if doc.get("breadcrumbs") == breadcrumbs:
        return False
    doc["breadcrumbs"] = breadcrumbs
    yaml.sort_keys = sort_keys
    write_yaml(data, fp)
    return True


def _write_markdown_breadcrumbs(
    fp: Path, breadcrumbs: list[dict[str, str]], sort_keys: bool
) -> bool:
    """Update ``doc.breadcrumbs`` in Markdown frontmatter of *fp*."""

    text = fp.read_text(encoding="utf-8") if fp.exists() else ""
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        buf = StringIO()
        yaml.sort_keys = sort_keys
        yaml.dump({"doc": {"breadcrumbs": breadcrumbs}}, buf)
        dumped = buf.getvalue()
        new_lines = ["---\n", dumped, "---\n"] + lines
        fp.write_text("".join(new_lines), encoding="utf-8")
        return True

    end = None
    for idx in range(1, len(lines)):
        if lines[idx].startswith("---"):
            end = idx
            break
    if end is None:
        return False
    frontmatter = "".join(lines[1:end])
    data = yaml.load(frontmatter) or {}
    doc = data.setdefault("doc", {})
    if doc.get("breadcrumbs") == breadcrumbs:
        return False
    doc["breadcrumbs"] = breadcrumbs
    buf = StringIO()
    yaml.sort_keys = sort_keys
    yaml.dump(data, buf)
    lines[1:end] = [buf.getvalue()]
    fp.write_text("".join(lines), encoding="utf-8")
    return True


def _write_breadcrumbs(
    fp: Path, breadcrumbs: list[dict[str, str]], sort_keys: bool
) -> bool:
    """Update ``doc.breadcrumbs`` in *fp* and return ``True`` when changed."""

    if fp.suffix in YAML_EXTS:
        return _write_yaml_breadcrumbs(fp, breadcrumbs, sort_keys)
    if fp.suffix == ".md":
        return _write_markdown_breadcrumbs(fp, breadcrumbs, sort_keys)
    return False


def update_directory(
    root: Path, sort_keys: bool = False
) -> tuple[list[str], int]:
    """Update breadcrumbs for all metadata files under *root*.

    Returns ``(messages, checked)`` where ``messages`` contains log entries for
    modified files and ``checked`` is the number of files examined.
    """

    messages: list[str] = []
    checked = 0

    for base, path, metadata in _iter_metadata_files(root):
        if metadata is None:
            continue
        doc = metadata.get("doc") if isinstance(metadata, dict) else None
        existing = _normalise_breadcrumbs(doc.get("breadcrumbs") if isinstance(doc, dict) else None)
        expected = _expected_breadcrumbs(base, root, existing)
        if existing == expected:
            continue

        file_paths: set[Path] = {path}
        if isinstance(metadata.get("path"), list):
            for p in metadata["path"]:
                candidate = Path(p)
                if candidate.is_absolute():
                    try:
                        candidate = candidate.relative_to(Path.cwd())
                    except ValueError:
                        pass
                file_paths.add(candidate)

        yaml_files = [fp for fp in file_paths if fp.suffix in YAML_EXTS]
        targets = yaml_files or sorted(file_paths)

        for fp in targets:
            if not fp.exists():
                continue
            checked += 1
            if _write_breadcrumbs(fp, expected, sort_keys):
                resolved = fp.resolve()
                try:
                    rel = resolved.relative_to(Path.cwd())
                    rel_text = str(rel)
                except ValueError:
                    rel_text = str(resolved)
                msg = f"{rel_text}: breadcrumbs updated"
                logger.info(msg)
                messages.append(msg)

    return messages, checked


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``update-breadcrumbs`` console script."""

    args = parse_args(argv)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.log)

    root_path = Path(args.path)
    if not root_path.exists():
        logger.error("Directory does not exist", path=str(root_path))
        return 1

    if root_path.is_absolute():
        try:
            root = root_path.relative_to(Path.cwd())
        except ValueError:
            logger.error("Directory must be within the current workspace", path=str(root_path))
            return 1
    else:
        root = root_path

    logger.debug("Scanning directory", root=str(root_path.resolve()))
    messages, checked = update_directory(root, args.sort_keys)
    logger.info("Summary", checked=checked, changed_count=len(messages))
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
