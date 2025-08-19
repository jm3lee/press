#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from pie.cli import create_parser
from pie.logging import logger, configure_logging

from pie.index_tree import walk, getopt_link, getopt_show


def _collect_ids(directory: Path) -> list[str]:
    """Return all document ids under *directory*."""
    ids: list[str] = []
    for meta, path in walk(directory):
        ids.append(meta["id"])
        if path.is_dir():
            ids.extend(_collect_ids(path))
    return ids


def _build_id_map(ids: list[str]) -> dict[str, str]:
    """Return mapping of full ids to shortest unique prefixes."""
    if not ids:
        return {}

    unique_ids = set(ids)
    max_len = max(len(i) for i in unique_ids)
    for length in range(1, max_len + 1):
        prefixes = {i: i[:length] for i in unique_ids}
        # Increase the prefix length until all ids map to unique prefixes
        if len(set(prefixes.values())) == len(unique_ids):
            return prefixes
    return {i: i for i in unique_ids}


def _log_id_map(id_map: dict[str, str], output_file: Path | str | None = None) -> None:
    """Write *id_map* to ``<output_file>.map.json`` or ``short_ids.map.json``."""
    log_path = (
        Path(f"{output_file}.map.json") if output_file else Path("short_ids.map.json")
    )
    log_path.write_text(json.dumps(id_map, indent=2), encoding="utf-8")
    logger.info("Short id map written to {}", log_path)


def process_dir(
    directory: Path,
    id_map: dict[str, str] | None = None,
    map_target: Path | str | None = None,
):
    """Recursively process *directory* to yield structured entries.

    If *id_map* is ``None``, a map of full ids to their shortest unique prefixes is
    built and written to ``<map_target>.map.json`` (or ``short_ids.map.json`` when
    *map_target* is ``None``).
    """
    if id_map is None:
        id_map = _build_id_map(_collect_ids(directory))
        _log_id_map(id_map, map_target)

    entries = list(walk(directory))
    for meta, path in entries:
        if "title" not in meta:
            raise ValueError(f"Missing 'title' in {path}")
    entries.sort(key=lambda x: x[0]["title"].lower())
    for meta, path in entries:
        entry_id = id_map.get(meta["id"], meta["id"])
        entry_title = meta["title"]
        entry_url = meta.get("url")
        entry_link = getopt_link(meta)
        entry_show = getopt_show(meta)
        if path.is_dir():
            children = list(process_dir(path, id_map, map_target))
            if entry_show:
                node = {"id": entry_id, "label": entry_title, "children": children}
                if entry_link and entry_url:
                    node["url"] = entry_url
                yield node
            else:
                yield from children
        else:
            if entry_show:
                node = {"id": entry_id, "label": entry_title}
                if entry_link and entry_url:
                    node["url"] = entry_url
                yield node


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = create_parser("Generate JSON index from metadata tree")
    parser.add_argument("root", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("output", nargs="?", help="Write JSON to file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.verbose or args.log:
        configure_logging(args.verbose, args.log)

    root_dir = Path(args.root)
    try:
        data = list(process_dir(root_dir, map_target=args.output))
    except ValueError as exc:
        logger.error(str(exc))
        raise SystemExit(1)

    json_data = json.dumps(data, indent=2)
    if args.output:
        Path(args.output).write_text(json_data, encoding="utf-8")
    else:
        print(json_data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
