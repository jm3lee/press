"""
Generate Makefile rules for processing ``.yml`` files with ``pandoc``.

By default the script scans the ``src`` directory and writes rules that
produce preprocessed ``.md`` and rendered ``.html`` files under ``build``.
Both the source root and build root can be overridden via function
parameters or command–line arguments.
"""

import argparse
import sys
from pathlib import Path

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

    return f"""
{preprocessed_yml}: {input_path}
	emojify < $< > $@
{output_html}: {preprocessed_md} {preprocessed_yml}
	$(PANDOC_CMD) $(PANDOC_OPTS) --metadata-file={preprocessed_yml} -o $@ $<
	python3 -m pie.error_on_python_dict $@
"""


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


if __name__ == "__main__":
    main()
