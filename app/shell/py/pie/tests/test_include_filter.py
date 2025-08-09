from __future__ import annotations

from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pie.include_filter as include_filter


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


def test_include_deflist_entry_writes_entries(tmp_path, monkeypatch):
    """include_deflist_entry inserts dt/dd pairs for files."""
    a = tmp_path / "a.md"
    a.write_text("---\nskip: yes\n---\nA\n", encoding="utf-8")
    b = tmp_path / "b.md"
    b.write_text("B\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    include_filter.outfile = StringIO()

    def fake_meta(path: str, key: str):
        data = {
            "a.md": {"title": "Title A", "url": "http://a"},
            "b.md": {"title": "Title B", "url": None},
        }
        return data.get(path, {}).get(key)

    with patch("pie.include_filter.get_metadata_by_path", side_effect=fake_meta):
        include_filter.include_deflist_entry("a.md", "b.md")
    try:
        assert (
            include_filter.outfile.getvalue()
            == '<dt>Title A <a href="http://a">↗</a></dt>\n<dd>\nA\n</dd>\n'
            + '<dt>Title B</dt>\n<dd>\nB\n</dd>\n'
        )
    finally:
        include_filter.outfile = None


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


def test_parse_args_parses_positions():
    """parse_args returns expected positional arguments."""
    args = include_filter.parse_args(["out", "in.md", "out.md"])
    assert (args.outdir, args.infile, args.outfile) == ("out", "in.md", "out.md")
