import os
import io
import runpy
import sys
from unittest import mock

import pytest

from pie import include_filter


def test_parse_metadata_returns_dict():
    """Front matter -> metadata dict."""
    include_filter.outfile = io.StringIO()
    f = io.StringIO("---\n{\"title\": \"Foo\"}\n---\nBody")
    data = include_filter.parse_metadata_or_print_first_line(f)
    assert data == {"title": "Foo"}
    assert include_filter.outfile.getvalue() == ""


def test_parse_metadata_prints_line():
    """No front matter -> first line output."""
    out = io.StringIO()
    include_filter.outfile = out
    f = io.StringIO("First line\nSecond")
    data = include_filter.parse_metadata_or_print_first_line(f)
    assert data is None
    assert out.getvalue() == "First line\n"


def test_md_to_html_links():
    """'.md' links -> '.html' links."""
    line = "See [Doc](dist/docs/guides/file.md) and [X](x.md)"
    converted = include_filter.md_to_html_links(line)
    assert converted == "See [Doc](dist/docs/guides/file.html) and [X](x.html)"


def test_new_filestem_skips_existing(tmp_path):
    """Find next available stem like diagram2."""
    (tmp_path / "diagram0.svg").write_text("")
    (tmp_path / "diagram1.mmd").write_text("")
    stem = include_filter.new_filestem(str(tmp_path / "diagram"))
    assert stem == str(tmp_path / "diagram2")


def test_include_writes_output(tmp_path):
    """include() writes processed markdown."""
    md = tmp_path / "doc.md"
    md.write_text("---\n{\"title\": \"Title\"}\n---\n# H1\nText\n")
    include_filter.outfile = io.StringIO()
    include_filter.heading_level = 0
    include_filter.include(str(md))
    expected = "# Title\n# H1\nText\n"
    assert include_filter.outfile.getvalue() == expected


def test_mermaid_creates_files(tmp_path):
    """Mermaid block -> .mmd and .png files."""
    include_filter.figcount = 0
    include_filter.outdir = str(tmp_path)
    include_filter.outfile = io.StringIO()

    mmd = tmp_path / "src.mmd"
    mmd.write_text("preamble\n```mermaid\nA-->B\n```\n")

    with mock.patch("pie.include_filter.new_filestem", return_value=str(tmp_path / "diagram0")) as nf, \
         mock.patch("os.system") as os_sys:
        include_filter.mermaid(str(mmd), "alt", "#id")

    os_sys.assert_called_once_with(f"npx mmdc -i {tmp_path/'diagram0.mmd'} -o {tmp_path/'diagram0.png'}")
    assert (tmp_path / "diagram0.mmd").read_text() == "A-->B\n"
    assert include_filter.outfile.getvalue().strip() == f"![alt](./diagram0.png){{ #id }}"
    assert include_filter.figcount == 1


def test_main_writes_log_file(tmp_path):
    """CLI writes output and log."""
    outdir = tmp_path / "out"
    outdir.mkdir()
    infile = tmp_path / "doc.md"
    infile.write_text("Hello")
    outfile = tmp_path / "out.md"
    log = tmp_path / "inc.log"

    include_filter.main([
        str(outdir),
        str(infile),
        str(outfile),
        "--log",
        str(log),
    ])

    assert outfile.exists()
    assert log.exists()


def test_yield_lines_reads_until_fence():
    """yield_lines stops before ``` fence."""
    f = io.StringIO("one\ntwo\n```\nthree\n")
    lines = list(include_filter.yield_lines(f))
    assert lines == ["one\n", "two\n"]
    assert f.readline() == "three\n"


def test_parse_args_parses_all_options():
    """parse_args reads outdir, infile, outfile, log."""
    args = include_filter.parse_args([
        "out", "in.md", "out.md", "--log", "log.txt"
    ])
    assert args.outdir == "out"
    assert args.infile == "in.md"
    assert args.outfile == "out.md"
    assert args.log == "log.txt"


def test_include_deflist_entry_handles_files_and_dirs(tmp_path):
    """Files + directory -> combined <dt>/<dd> output."""
    f1 = tmp_path / "a.md"
    f1.write_text("---\n{\"title\": \"A\"}\n---\nA body\n")
    sub = tmp_path / "sub"
    sub.mkdir()
    f2 = sub / "b.md"
    f2.write_text("---\n{}\n---\nB body\n")
    include_filter.outfile = io.StringIO()
    include_filter.include_deflist_entry(str(f1), str(sub))
    expected = "<dt>A</dt>\n<dd>\nA body\n</dd>\n<dd>\nB body\n</dd>\n"
    assert include_filter.outfile.getvalue() == expected


def test_include_deflist_entry_sort_fn(tmp_path):
    """Custom sort_fn orders entries descending."""
    f1 = tmp_path / "a.md"
    f1.write_text("---\n{\"title\": \"A\"}\n---\nA\n")
    f2 = tmp_path / "b.md"
    f2.write_text("---\n{\"title\": \"B\"}\n---\nB\n")
    include_filter.outfile = io.StringIO()
    include_filter.include_deflist_entry(
        str(f1),
        str(f2),
        sort_fn=lambda files: sorted(files, key=lambda p: p.name, reverse=True),
    )
    expected = "<dt>B</dt>\n<dd>\nB\n</dd>\n<dt>A</dt>\n<dd>\nA\n</dd>\n"
    assert include_filter.outfile.getvalue() == expected


def test_main_executes_lines_individually_and_tracks_headings(tmp_path):
    """Main runs each line; heading_level increments."""
    outdir = tmp_path / "out"
    outdir.mkdir()
    infile = tmp_path / "doc.md"
    infile.write_text("# H1\n```python\n1\n2\n```\n")
    outfile = tmp_path / "out.md"
    include_filter.heading_level = 0
    include_filter.main([str(outdir), str(infile), str(outfile)])
    assert outfile.read_text() == "# H1\n"
    assert include_filter.heading_level == 1


def test_script_entry_point(tmp_path, monkeypatch):
    """Running module executes main."""
    outdir = tmp_path / "out"
    outdir.mkdir()
    infile = tmp_path / "doc.md"
    infile.write_text("Hello")
    outfile = tmp_path / "out.md"
    monkeypatch.setattr(sys, "argv", [
        "include_filter.py",
        str(outdir),
        str(infile),
        str(outfile),
    ])
    runpy.run_module("pie.include_filter", run_name="__main__")
    assert outfile.read_text() == "Hello"

