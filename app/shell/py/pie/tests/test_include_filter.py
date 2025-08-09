import os
import io
import runpy
import sys
from pathlib import Path
from unittest import mock
import types

import pytest

# Stub optional dependencies used by include_filter.

def _stub_add(sink, *a, **k):
    if isinstance(sink, (str, os.PathLike)):
        Path(sink).touch()

stub_logger = types.SimpleNamespace(
    remove=lambda *a, **k: None,
    add=_stub_add,
    info=lambda *a, **k: None,
    debug=lambda *a, **k: None,
)
sys.modules.setdefault("loguru", types.SimpleNamespace(logger=stub_logger))
sys.modules.setdefault(
    "pie.render_jinja_template", types.SimpleNamespace(get_cached_metadata=lambda *a, **k: None)
)

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


def test_skip_front_matter_skips_block():
    f = io.StringIO("---\na: b\n---\nbody\n")
    include_filter._skip_front_matter(f)
    assert f.readline() == "body\n"


def test_skip_front_matter_rewinds_without_block():
    f = io.StringIO("no front matter\nsecond\n")
    include_filter._skip_front_matter(f)
    assert f.readline() == "no front matter\n"


def test_include_deflist_entry_outputs_expected_html(tmp_path):
    file_with_front = tmp_path / "b.md"
    file_with_front.write_text("---\n---\ncontent1\n")
    file_plain = tmp_path / "a.md"
    file_plain.write_text("content2\n")

    out = io.StringIO()
    include_filter.outfile = out

    def fake_metadata(path: Path):
        if Path(path).name == "a.md":
            return {"title": "A", "url": "http://a"}
        else:
            return {"title": "B"}

    with mock.patch("pie.include_filter.load_metadata_pair", side_effect=fake_metadata):
        include_filter.include_deflist_entry(str(tmp_path))

    expected = (
        "<dt>A <a href=\"http://a\">↗</a></dt>\n"
        "<dd>\ncontent2\n</dd>\n"
        "<dt>B</dt>\n"
        "<dd>\ncontent1\n</dd>\n"
    )
    assert out.getvalue() == expected


def test_include_deflist_entry_respects_sort_fn(tmp_path):
    file_a = tmp_path / "a.md"
    file_a.write_text("A\n")
    file_b = tmp_path / "b.md"
    file_b.write_text("B\n")

    out = io.StringIO()
    include_filter.outfile = out

    with mock.patch("pie.include_filter.load_metadata_pair", return_value=None):
        include_filter.include_deflist_entry(
            str(file_a), str(file_b), sort_fn=lambda files: reversed(sorted(files))
        )

    assert out.getvalue() == "<dd>\nB\n</dd>\n<dd>\nA\n</dd>\n"

