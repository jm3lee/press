import os
import io
from unittest import mock

import pytest

from pie import include_filter


def test_parse_metadata_returns_dict():
    include_filter.outfile = io.StringIO()
    f = io.StringIO("---\n{\"title\": \"Foo\"}\n---\nBody")
    data = include_filter.parse_metadata_or_print_first_line(f)
    assert data == {"title": "Foo"}
    assert include_filter.outfile.getvalue() == ""


def test_parse_metadata_prints_line():
    out = io.StringIO()
    include_filter.outfile = out
    f = io.StringIO("First line\nSecond")
    data = include_filter.parse_metadata_or_print_first_line(f)
    assert data is None
    assert out.getvalue() == "First line\n"


def test_md_to_html_links():
    line = "See [Doc](dist/docs/file.md) and [X](x.md)"
    converted = include_filter.md_to_html_links(line)
    assert converted == "See [Doc](dist/docs/file.html) and [X](x.html)"


def test_new_filestem_skips_existing(tmp_path):
    (tmp_path / "diagram0.svg").write_text("")
    (tmp_path / "diagram1.mmd").write_text("")
    stem = include_filter.new_filestem(str(tmp_path / "diagram"))
    assert stem == str(tmp_path / "diagram2")


def test_include_writes_output(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("---\n{\"title\": \"Title\"}\n---\n# H1\nText\n")
    include_filter.outfile = io.StringIO()
    include_filter.heading_level = 0
    include_filter.include(str(md))
    expected = "# Title\n# H1\nText\n"
    assert include_filter.outfile.getvalue() == expected


def test_mermaid_creates_files(tmp_path):
    include_filter.figcount = 0
    include_filter.outdir = str(tmp_path)
    include_filter.outfile = io.StringIO()

    mmd = tmp_path / "src.mmd"
    mmd.write_text("```mermaid\nA-->B\n```\n")

    with mock.patch("pie.include_filter.new_filestem", return_value=str(tmp_path / "diagram0")) as nf, \
         mock.patch("os.system") as os_sys:
        include_filter.mermaid(str(mmd), "alt", "#id")

    os_sys.assert_called_once_with(f"npx mmdc -i {tmp_path/'diagram0.mmd'} -o {tmp_path/'diagram0.png'}")
    assert (tmp_path / "diagram0.mmd").read_text() == "A-->B\n"
    assert include_filter.outfile.getvalue().strip() == f"![alt](./diagram0.png){{ #id }}"
    assert include_filter.figcount == 1


def test_main_writes_log_file(tmp_path):
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
    f = io.StringIO("one\ntwo\n```\nthree\n")
    lines = list(include_filter.yield_lines(f))
    assert lines == ["one\n", "two\n"]
    assert f.readline() == "three\n"


def test_parse_args_parses_all_options():
    args = include_filter.parse_args([
        "out", "in.md", "out.md", "--log", "log.txt"
    ])
    assert args.outdir == "out"
    assert args.infile == "in.md"
    assert args.outfile == "out.md"
    assert args.log == "log.txt"
