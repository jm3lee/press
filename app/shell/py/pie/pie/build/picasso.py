"""
Generate Makefile rules for processing metadata files with ``pandoc``.

By default the script scans the ``src`` directory and writes rules that
produce preprocessed ``.md`` and rendered ``.html`` files under ``build``.
Both the source root and build root can be overridden via function
parameters or command–line arguments. The script also emits dependency
rules for cross-document links and ``include-filter`` directives so that
changes to referenced files trigger a rebuild.
"""

import argparse
import ast
from collections import defaultdict
import re
import sys
from pathlib import Path
from typing import Callable, Iterable

from pie.logging import logger, add_log_argument, configure_logging
from pie.metadata import load_metadata_pair

# WARNING: picasso generates build rules; cannot rely on redis updates because
# redis updates rely on the build infrastructure to work

_TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "picasso.rule.mk.jinja"
_RULE_TEMPLATE = _TEMPLATE_PATH.read_text()


def generate_rule(
    input_path: Path,
    src_root: Path = Path("src"),
    build_root: Path = Path("build"),
) -> str:
    """Generate a Makefile rule for a given metadata file.

    Args:
        input_path (Path): Path to the source metadata file.
        src_root (Path): Directory that contains the source files.
        build_root (Path): Directory where build artifacts are written.

    Returns:
        str: A multi-line string defining the Makefile rule.

    Example:
        >>> from pathlib import Path
        >>> print(generate_rule(Path("src/foo/bar.yml")))
        build/foo/bar.yml: src/foo/bar.yml
            $(call status,Preprocess $<)
            $(Q)mkdir -p $(dir build/foo/bar.yml)
            $(Q)cp $< $@
        build/foo/bar.html: build/foo/bar.md build/foo/bar.yml $(PANDOC_TEMPLATE) $(BUILD_DIR)/.process-yamls
            $(call status,Generate HTML $@)
            $(Q)$(PANDOC_CMD) $(PANDOC_OPTS) --template=$(PANDOC_TEMPLATE) --metadata-file=build/foo/bar.yml -o $@ $<
            $(Q)check-bad-jinja-output $@
    """
    # Compute the path of ``input_path`` relative to the source root
    relative = input_path.relative_to(src_root)

    # Build output paths under ``build_root`` while preserving directory layout
    output_html = (build_root / relative.with_suffix(".html")).as_posix()
    preprocessed_md = (build_root / relative.with_suffix(".md")).as_posix()
    preprocessed_yml = (build_root / relative.with_suffix(".yml")).as_posix()

    preprocess_cmd = "cp $< $@"
    metadata = load_metadata_pair(input_path)
    tmpl = None
    if metadata:
        pandoc_meta = metadata.get("pandoc")
        if isinstance(pandoc_meta, dict):
            tmpl = pandoc_meta.get("template")
    template = Path(tmpl).as_posix() if tmpl else None

    template_dep = template or "$(PANDOC_TEMPLATE)"
    template_arg = f"--template={template_dep}" if template else "--template=$(PANDOC_TEMPLATE)"

    rule = _RULE_TEMPLATE.format(
        input_path=input_path.as_posix(),
        preprocessed_yml=preprocessed_yml,
        output_html=output_html,
        preprocessed_md=preprocessed_md,
        template_dep=template_dep,
        template_arg=template_arg,
        preprocess_cmd=preprocess_cmd,
    )
    return f"\n{rule}"


LINK_RE = re.compile(r"\{\{\s*[\"']([^\"']+)[\"']\s*\|\s*link[\w]*")
LINK_GLOBAL_RE = re.compile(r"\{\{\s*link[\w]*\(\s*[\"']([^\"']+)[\"']")
PY_BLOCK_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)
INCLUDE_RE = re.compile(r"(include(?:_deflist_entry)?)\(\s*([^)]*)\)")


def collect_ids(src_root: Path) -> dict[str, Path]:
    """Return a mapping of metadata ``id`` values to source files."""

    id_map: dict[str, Path] = {}
    processed: set[Path] = set()

    for path in src_root.rglob("*"):
        if path.suffix.lower() not in {".md", ".yml", ".yaml"}:
            continue

        base = path.with_suffix("")
        if base in processed:
            continue
        processed.add(base)

        doc_id = None
        try:
            metadata = load_metadata_pair(path)
            if metadata:
                doc_id = metadata.get("id")
        except Exception:
            logger.warning("Failed to parse metadata", file=str(path))

        if not doc_id:
            doc_id = path.stem

        id_map[doc_id] = path

    return id_map


def _has_path(
    graph: dict[str, set[str]], start: str, target: str, seen: set[str]
) -> bool:
    """Return True if *target* is reachable from *start* in *graph*."""

    if start == target:
        return True
    if start in seen:
        return False
    seen.add(start)
    for nxt in graph.get(start, set()):
        if _has_path(graph, nxt, target, seen):
            return True
    return False


def _remove_circular_dependencies(rules: set[str]) -> list[str]:
    """Remove rules that would introduce circular dependencies."""

    graph: dict[str, set[str]] = defaultdict(set)
    result: list[str] = []
    for rule in sorted(rules):
        if ":" not in rule:
            result.append(rule)
            continue
        src, dep = [s.strip() for s in rule.split(":", 1)]
        if _has_path(graph, dep, src, set()):
            logger.warning("Circular dependency detected", rule=rule)
            continue
        graph[src].add(dep)
        result.append(rule)
    return result


def _resolve_include_paths(
    func: str,
    arglist: str,
    *,
    src_build: Path,
    src_root: Path,
    build_root: Path,
    build_path: Callable[[Path], str],
) -> list[str]:
    """Return dependency rules for an ``include``/``include_deflist_entry`` call.

    ``generate_dependencies`` previously inlined this logic; extracting it makes
    the path handling easier to reason about and unit test.  ``func`` is the
    function name (``include`` or ``include_deflist_entry``) and ``arglist`` is
    the raw argument string captured by ``INCLUDE_RE``.
    """

    logger.debug(
        "Resolving include paths",
        func=func,
        arglist=arglist,
        src_build=src_build.as_posix(),
        src_root=src_root.as_posix(),
        build_root=build_root.as_posix(),
    )

    try:
        call = ast.parse(f"f({arglist})", mode="eval").body
    except SyntaxError:
        # Ignore malformed Python blocks such as ``include('a', bad=)``.
        logger.debug("Malformed include statement", arglist=arglist)
        return []

    # Extract positional string arguments and optional ``glob`` keyword.
    paths = [
        arg.value
        for arg in call.args
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
    ]

    glob = "*"
    if func == "include_deflist_entry":
        for kw in call.keywords:
            if (
                kw.arg == "glob"
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
            ):
                glob = kw.value.value
                break
    logger.debug("Parsed include arguments", paths=paths, glob=glob)

    src_build_str = src_build.as_posix()
    build_root_str = build_root.as_posix()

    def iter_targets(path: Path) -> Iterable[Path]:
        """Yield files referenced by ``path`` (directory or single file)."""

        if path.is_dir():
            pattern = glob if func == "include_deflist_entry" else "*"
            yield from (p for p in path.rglob(pattern) if p.is_file())
        else:
            yield path

    def resolve(dep: Path) -> tuple[Iterable[Path], bool]:
        dep_str = dep.as_posix()
        is_build = dep.is_absolute() or dep_str.startswith(build_root_str)
        logger.debug("Evaluating dependency", dep=dep_str, is_build=is_build)
        if not is_build:
            # Resolve relative paths against ``src_root``. ``include('src/foo')``
            # is treated the same as ``include('foo')``.
            if dep.parts and dep.parts[0] == src_root.name:
                dep = src_root / Path(*dep.parts[1:])
                logger.debug(
                    "Resolved with src_root prefix",
                    original=dep_str,
                    resolved=dep.as_posix(),
                )
            else:
                dep = src_root / dep
                logger.debug(
                    "Resolved relative path",
                    original=dep_str,
                    resolved=dep.as_posix(),
                )
        return iter_targets(dep), is_build

    rules: list[str] = []
    for dep in map(Path, paths):
        targets, is_build = resolve(dep)
        for target in targets:
            target_str = target.as_posix()
            if not is_build:
                target_str = (
                    Path(build_path(target)).with_suffix(target.suffix).as_posix()
                )
            rule = f"{src_build_str}: {target_str}"
            logger.debug("Adding include dependency", rule=rule, is_build=is_build)
            rules.append(rule)

    logger.debug("Resolved rules", count=len(rules))
    return rules


def _build_path(p: Path, *, src_root: Path, build_root: Path) -> str:
    """Return the build path for *p* relative to *src_root* and *build_root*."""

    rel = p.relative_to(src_root)
    out = build_root / rel
    if build_root.is_absolute():
        out = Path(build_root.name) / rel
    return out.as_posix()


def _file_dependencies(
    path: Path,
    text: str,
    id_map: dict[str, Path],
    *,
    src_root: Path,
    build_root: Path,
) -> set[str]:
    """Return dependency rules for a single source file."""

    build = lambda p: _build_path(p, src_root=src_root, build_root=build_root)
    src_build = Path(build(path)).with_suffix(path.suffix)
    rules: set[str] = set()

    # Jinja link references like {{"id"|link}} or {{link("id")}}
    ref_ids = LINK_RE.findall(text) + LINK_GLOBAL_RE.findall(text)
    for ref_id in ref_ids:
        ref_path = id_map.get(ref_id)
        if ref_path is None:
            continue
        dep_build = Path(build(ref_path)).with_suffix(ref_path.suffix)
        rules.add(f"{src_build.as_posix()}: {dep_build.as_posix()}")

    # ``include-filter`` blocks such as include("file.md")
    for block in PY_BLOCK_RE.findall(text):
        for func, arglist in INCLUDE_RE.findall(block):
            rules.update(
                _resolve_include_paths(
                    func,
                    arglist,
                    src_build=src_build,
                    src_root=src_root,
                    build_root=build_root,
                    build_path=build,
                )
            )

    return rules


def generate_dependencies(src_root: Path, build_root: Path) -> list[str]:
    """Return Makefile dependency rules based on Jinja links and include blocks."""

    id_map = collect_ids(src_root)
    rules: set[str] = set()

    for path in src_root.rglob("*"):
        if path.suffix.lower() not in {".md", ".yml", ".yaml"}:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            logger.warning("Failed to read file", file=str(path))
            continue

        rules.update(
            _file_dependencies(
                path,
                text,
                id_map,
                src_root=src_root,
                build_root=build_root,
            )
        )

    return _remove_circular_dependencies(rules)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Generate Makefile rules for processing metadata files with pandoc",
    )
    parser.add_argument(
        "--src",
        default="src",
        help="Directory containing source metadata files",
    )
    parser.add_argument(
        "--build",
        default="build",
        help="Directory where build artifacts are written",
    )
    add_log_argument(parser)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point: print Makefile rules for metadata files under ``src_root``."""

    args = parse_args(argv)
    configure_logging(args.verbose, args.log)
    src_root = Path(args.src)
    build_root = Path(args.build)

    if not src_root.is_dir():
        logger.error("Directory does not exist", directory=str(src_root))
        sys.exit(1)

    for path in sorted(src_root.rglob("*")):
        if path.suffix.lower() in {".yml", ".yaml"}:
            print(generate_rule(path, src_root=src_root, build_root=build_root))

    for rule in generate_dependencies(src_root, build_root):
        print(rule)


if __name__ == "__main__":
    main()
