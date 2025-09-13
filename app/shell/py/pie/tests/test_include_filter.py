from __future__ import annotations

from io import StringIO
from pathlib import Path
from unittest.mock import patch
import runpy
import sys
import importlib

import pie.filter.include as include_filter


def test_parse_metadata_or_print_first_line_parses_front_matter(tmp_path):
    """Front matter is returned and not written to outfile."""
    doc = tmp_path / "doc.md"
    doc.write_text("---\ntitle: Test\n---\nbody\n", encoding="utf-8")

    include_filter.outfile = StringIO()
    with doc.open("r", encoding="utf-8") as f:
        meta = include_filter.parse_metadata_or_print_first_line(f)
        remaining = f.readline()
    try:
        assert meta == {"title": "Test"}
        assert include_filter.outfile.getvalue() == ""
        assert remaining == "body\n"
    finally:
        include_filter.outfile = None


def test_parse_metadata_or_print_first_line_echoes_first_line(tmp_path):
    """No front matter -> first line echoed to outfile."""
    doc = tmp_path / "doc.md"
    doc.write_text("first\nsecond\n", encoding="utf-8")

    include_filter.outfile = StringIO()
    with doc.open("r", encoding="utf-8") as f:
        meta = include_filter.parse_metadata_or_print_first_line(f)
        remaining = f.readline()
    try:
        assert meta is None
        assert include_filter.outfile.getvalue() == "first\n"
        assert remaining == "second\n"
    finally:
        include_filter.outfile = None


def test_include_inserts_title_and_adjusts_headings(tmp_path):
    """include() writes heading and adjusts nested headings."""
    sub = tmp_path / "sub.md"
    sub.write_text("---\ntitle: Subdoc\n---\n# Subtitle\ntext\n", encoding="utf-8")

    include_filter.outfile = StringIO()
    include_filter.heading_level = 2
    include_filter.include(sub.as_posix())
    try:
        assert include_filter.outfile.getvalue() == "### Subdoc\n### Subtitle\ntext\n"
    finally:
        include_filter.outfile = None
        include_filter.heading_level = 0


def test_yield_lines_stops_at_code_fence():
    """yield_lines stops when encountering a closing fence."""
    f = StringIO("a\nb\n```\nrest\n")
    lines = list(include_filter.yield_lines(f))
    assert lines == ["a\n", "b\n"]
    assert f.readline() == "rest\n"


def test_new_filestem_skips_existing(tmp_path):
    """new_filestem increments counter until a free name is found."""
    (tmp_path / "diagram0.svg").write_text("", encoding="utf-8")
    (tmp_path / "diagram1.mmd").write_text("", encoding="utf-8")
    stem = tmp_path / "diagram"
    result = include_filter.new_filestem(str(stem))
    assert result == str(tmp_path / "diagram2")


def test_md_to_html_links_rewrites_extension():
    """Links ending in .md are rewritten to .html."""
    line = "See [A](a.md) and [B](http://ex/b.md)"
    assert (
        include_filter.md_to_html_links(line)
        == "See [A](a.html) and [B](http://ex/b.html)"
    )


def test_execute_python_block_executes_all_lines():
    """execute_python_block runs multiple statements in order."""

    include_filter.outfile = StringIO()
    include_filter.execute_python_block(
        [
            "a = 1\n",
            "b = 2\n",
            "print(a + b, file=outfile)\n",
        ]
    )
    try:
        assert include_filter.outfile.getvalue() == "3\n"
    finally:
        include_filter.outfile = None


def test_parse_args_parses_positions():
    """parse_args returns expected positional arguments."""
    args = include_filter.parse_args(["out", "in.md", "out.md"])
    assert (args.outdir, args.infile, args.outfile) == ("out", "in.md", "out.md")


def test_mermaid_writes_image_reference(tmp_path, monkeypatch):
    """mermaid() exports diagram and writes a reference."""
    src = tmp_path / "src.mmd"
    src.write_text("```mermaid\nA-->B\n```\n", encoding="utf-8")
    include_filter.outfile = StringIO()
    include_filter.outdir = tmp_path.as_posix()
    include_filter.figcount = 0

    monkeypatch.setattr(include_filter, "new_filestem", lambda stem: str(tmp_path / "diagram"))
    with patch("pie.filter.include.os.system") as system:
        system.return_value = 0
        include_filter.mermaid(src.as_posix(), "Alt", "#id")
    try:
        assert include_filter.outfile.getvalue() == "![Alt](./diagram.png){ #id }\n"
        assert include_filter.figcount == 1
        assert (tmp_path / "diagram.mmd").read_text() == "A-->B\n"
    finally:
        include_filter.outfile = None


def test_main_processes_markdown(tmp_path):
    """Running the module as a script processes Markdown input."""
    in_md = tmp_path / "in.md"
    out_md = tmp_path / "out.md"
    in_md.write_text(
        "# Heading\n```python\nprint('py', file=outfile)\n```\n[link](doc.md)\n",
        encoding="utf-8",
    )
    argv = ["include.py", tmp_path.as_posix(), in_md.as_posix(), out_md.as_posix()]
    old_argv = sys.argv
    sys.argv = argv
    try:
        sys.modules.pop("pie.filter.include", None)
        runpy.run_module("pie.filter.include", run_name="__main__")
    finally:
        sys.argv = old_argv
        globals()["include_filter"] = importlib.import_module("pie.filter.include")
    assert out_md.read_text() == "# Heading\npy\n[link](doc.html)\n"
