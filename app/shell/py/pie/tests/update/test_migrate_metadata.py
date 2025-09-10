from pathlib import Path

from pie.update import migrate_metadata
from pie.yaml import yaml


def test_moves_fields_under_doc(tmp_path: Path, capsys) -> None:
    """Top-level fields are moved into ``doc``."""
    src = tmp_path / "src"
    src.mkdir()

    yml = src / "doc.yml"
    yml.write_text(
        "title: T\nauthor: A\npubdate: Jan 1, 2020\n"
        "link:\n  class: x\n"
        "citation: C\n"
        "breadcrumbs:\n  - title: Home\n",
        encoding="utf-8",
    )

    md = src / "doc.md"
    md.write_text(
        "---\ntitle: T\nauthor: A\npubdate: Jan 1, 2020\n"
        "link:\n  tracking: false\n"
        "citation: C\n"
        "breadcrumbs:\n  - title: Home\n---\n",
        encoding="utf-8",
    )

    migrate_metadata.main([str(src)])

    data = yaml.load(yml.read_text(encoding="utf-8"))
    assert data["doc"]["title"] == "T"
    assert data["doc"]["author"] == "A"
    assert data["doc"]["pubdate"] == "Jan 1, 2020"
    assert data["doc"]["link"] == {"class": "x"}
    assert data["doc"]["citation"] == "C"
    assert data["doc"]["breadcrumbs"] == [{"title": "Home"}]
    assert "title" not in data
    assert "author" not in data
    assert "pubdate" not in data
    assert "link" not in data
    assert "citation" not in data
    assert "breadcrumbs" not in data

    md_data = yaml.load(md.read_text(encoding="utf-8").split("---\n", 2)[1])
    assert md_data["doc"]["title"] == "T"
    assert md_data["doc"]["author"] == "A"
    assert md_data["doc"]["pubdate"] == "Jan 1, 2020"
    assert md_data["doc"]["link"] == {"tracking": False}
    assert md_data["doc"]["citation"] == "C"
    assert md_data["doc"]["breadcrumbs"] == [{"title": "Home"}]
    assert "title" not in md_data
    assert "citation" not in md_data
    assert "breadcrumbs" not in md_data

    out_lines = capsys.readouterr().out.strip().splitlines()
    assert f"{yml}: migrated" in out_lines
    assert f"{md}: migrated" in out_lines
    assert "2 files checked" in out_lines[-2]
    assert "2 files changed" in out_lines[-1]


def test_moves_header_includes_to_html_scripts(
    tmp_path: Path, capsys
) -> None:
    """`header_includes` moves under `html.scripts`."""
    src = tmp_path / "src"
    src.mkdir()

    yml = src / "doc.yml"
    yml.write_text(
        "header_includes:\n- <script src=\"app.js\"></script>\n",
        encoding="utf-8",
    )

    migrate_metadata.main([str(src)])

    data = yaml.load(yml.read_text(encoding="utf-8"))
    assert data["html"]["scripts"] == [
        "<script src=\"app.js\"></script>"
    ]
    assert "header_includes" not in data

    out_lines = capsys.readouterr().out.strip().splitlines()
    assert f"{yml}: migrated" in out_lines
    assert "1 file checked" in out_lines[-2]
    assert "1 file changed" in out_lines[-1]
