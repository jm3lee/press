"""
Generate Makefile rules for processing ``.yml`` files with ``pandoc``.

By default the script scans the ``src`` directory and writes rules that
produce preprocessed ``.md`` and rendered ``.html`` files under ``build``.
Both the source root and build root can be overridden via function
parameters or command–line arguments.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml
from pie.utils import add_file_logger, logger


def generate_rule(
    input_path: Path,
    src_root: Path = Path("src"),
    build_root: Path = Path("build"),
) -> str:
    """Generate a Makefile rule for a given YAML metadata file.

    Args:
        input_path (Path): Path to the source `.yml` file.
        src_root (Path): Directory that contains the source files.
        build_root (Path): Directory where build artifacts are written.

    Returns:
        str: A multi-line string defining the Makefile rule.

    Example:
        >>> from pathlib import Path
        >>> print(generate_rule(Path("src/foo/bar.yml")))
        build/foo/bar.html: build/foo/bar.md src/foo/bar.yml
            $(PANDOC_CMD) $(PANDOC_OPTS) --metadata-file=build/foo/bar.yml -o $@ $<
    """
    # Compute the path of ``input_path`` relative to the source root
    relative = input_path.relative_to(src_root)

    # Build output paths under ``build_root`` while preserving directory layout
    output_html = (build_root / relative.with_suffix(".html")).as_posix()
    preprocessed_md = (build_root / relative.with_suffix(".md")).as_posix()
    preprocessed_yml = (build_root / relative.with_suffix(".yml")).as_posix()

    return (
        f"\n"
        f"{preprocessed_yml}: {input_path}\n"
        f"\t$(Q)mkdir -p $(dir {preprocessed_yml})\n"
        f"\t$(Q)emojify < $< > $@\n"
        f"\t$(Q)process-yaml $< $@\n"
        f"{output_html}: {preprocessed_md} {preprocessed_yml}\n"
        f"\t$(Q)$(PANDOC_CMD) $(PANDOC_OPTS) --metadata-file={preprocessed_yml} -o $@ $<\n"
        f"\t$(Q)python3 -m pie.error_on_python_dict $@"
    )


LINK_RE = re.compile(r"\{\{\s*[\"']([^\"']+)[\"']\s*\|\s*link[\w]*")


def collect_ids(src_root: Path) -> dict[str, Path]:
    """Return a mapping of metadata ``id`` values to source files."""

    id_map: dict[str, Path] = {}

    for path in src_root.rglob("*"):
        if path.suffix.lower() in {".md", ".yml", ".yaml"}:
            doc_id = None
            try:
                if path.suffix.lower() == ".md":
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    if lines and lines[0].strip() == "---":
                        y = []
                        for line in lines[1:]:
                            if line.strip() == "---":
                                break
                            y.append(line)
                        data = yaml.safe_load("".join(y)) or {}
                        if isinstance(data, dict):
                            doc_id = data.get("id")
                else:
                    with open(path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                        if isinstance(data, dict):
                            doc_id = data.get("id")
            except Exception:
                logger.warning("Failed to parse metadata", file=str(path))

            if not doc_id:
                doc_id = path.stem

            id_map[doc_id] = path

    return id_map


def generate_dependencies(src_root: Path, build_root: Path) -> list[str]:
    """Return Makefile dependency rules based on Jinja link references."""

    id_map = collect_ids(src_root)
    rules: set[str] = set()

    def build_path(p: Path) -> str:
        rel = p.relative_to(src_root)
        out = build_root / rel
        if build_root.is_absolute():
            out = Path(build_root.name) / rel
        return out.as_posix()

    for path in src_root.rglob("*"):
        if path.suffix.lower() not in {".md", ".yml", ".yaml"}:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            logger.warning("Failed to read file", file=str(path))
            continue

        matches = LINK_RE.findall(text)
        if not matches:
            continue

        src_build = Path(build_path(path)).with_suffix(path.suffix)
        for ref_id in matches:
            ref_path = id_map.get(ref_id)
            if ref_path is None:
                continue
            dep_build = Path(build_path(ref_path)).with_suffix(ref_path.suffix)
            rules.add(f"{src_build.as_posix()}: {dep_build.as_posix()}")

    return sorted(rules)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Generate Makefile rules for processing YAML files with pandoc",
    )
    parser.add_argument(
        "--src",
        default="src",
        help="Directory containing source `.yml` files",
    )
    parser.add_argument(
        "--build",
        default="build",
        help="Directory where build artifacts are written",
    )
    parser.add_argument(
        "-l",
        "--log",
        help="Write logs to the specified file",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point: print Makefile rules for ``.yml`` files under ``src_root``."""

    args = parse_args(argv)
    if args.log:
        add_file_logger(args.log, level="DEBUG")
    src_root = Path(args.src)
    build_root = Path(args.build)

    if not src_root.is_dir():
        logger.error("Directory does not exist", directory=str(src_root))
        sys.exit(1)

    for yml_file in src_root.rglob("*.yml"):
        print(generate_rule(yml_file, src_root=src_root, build_root=build_root))

    for rule in generate_dependencies(src_root, build_root):
        print(rule)


if __name__ == "__main__":
    main()
