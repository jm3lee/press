"""
This script traverses the `src` directory for `.yml` files and generates
Makefile rules to process them with `pandoc`. Each `.yml` file produces
corresponding `.md` and `.html` targets in the `build` directory.
"""

import sys
from pathlib import Path


def generate_rule(input_path: Path) -> str:
    """Generate a Makefile rule for a given YAML metadata file.

    Args:
        input_path (Path): Path to the source `.yml` file.

    Returns:
        str: A multi-line string defining the Makefile rule.

    Example:
        >>> from pathlib import Path
        >>> print(generate_rule(Path("src/foo/bar.yml")))
        build/foo/bar.html: build/foo/bar.md src/foo/bar.yml
            $(PANDOC_CMD) $(PANDOC_OPTS) --metadata-file=src/foo/bar.yml -o $@ $<
    """
    # Build output paths under `build/`, preserving subdirectory structure
    output_html = input_path.with_suffix(".html").as_posix().replace("src/", "build/")
    preprocessed_md = input_path.with_suffix(".md").as_posix().replace("src/", "build/")
    preprocessed_yml = (
        input_path.with_suffix(".yml").as_posix().replace("src/", "build/")
    )

    return f"""
{preprocessed_yml}: {input_path}
	emojify < $< > $@
{output_html}: {preprocessed_md} {preprocessed_yml}
	$(PANDOC_CMD) $(PANDOC_OPTS) --metadata-file={preprocessed_yml} -o $@ $<
	python3 -m pie.error_on_python_dict $@
"""


def main() -> None:
    """Entry point: find all `.yml` files under `src/` and print Makefile rules."""
    src_root = Path("src")
    if not src_root.is_dir():
        sys.stderr.write(f"Directory {src_root!s} does not exist\n")
        sys.exit(1)

    for yml_file in src_root.rglob("*.yml"):
        print(generate_rule(yml_file))


if __name__ == "__main__":
    main()
