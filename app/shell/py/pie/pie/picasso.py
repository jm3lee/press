"""
Generate Makefile rules for processing ``.yml`` files with ``pandoc``.

By default the script scans the ``src`` directory and writes rules that
produce preprocessed ``.md`` and rendered ``.html`` files under ``build``.
Both the source root and build root can be overridden via function
parameters or command–line arguments.
"""

import sys
from pathlib import Path


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


def main(src_root: Path = Path("src"), build_root: Path = Path("build")) -> None:
    """Entry point: print Makefile rules for ``.yml`` files under ``src_root``."""

    if not src_root.is_dir():
        sys.stderr.write(f"Directory {src_root!s} does not exist\n")
        sys.exit(1)

    for yml_file in src_root.rglob("*.yml"):
        print(generate_rule(yml_file, src_root=src_root, build_root=build_root))


if __name__ == "__main__":
    argv = sys.argv[1:]
    src = Path(argv[0]) if len(argv) >= 1 else Path("src")
    build = Path(argv[1]) if len(argv) >= 2 else Path("build")
    main(src_root=src, build_root=build)
