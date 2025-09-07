from pathlib import Path

from pie.update import migrate_metadata
from pie.yaml import yaml


def test_moves_fields_under_doc(tmp_path: Path, capsys) -> None:
    """Top-level fields are moved into ``doc``."""
    src = tmp_path / "src"
    src.mkdir()

    yml = src / "doc.yml"
    yml.write_text(
        "title: T\nauthor: A\npubdate: Jan 1, 2020\nlink:\n  class: x\n",
        encoding="utf-8",
    )

    md = src / "doc.md"
    md.write_text(
        "---\ntitle: T\nauthor: A\npubdate: Jan 1, 2020\nlink:\n  tracking: false\n---\n",
        encoding="utf-8",
    )

    migrate_metadata.main([str(src)])

    data = yaml.load(yml.read_text(encoding="utf-8"))
    assert data["doc"]["title"] == "T"
    assert data["doc"]["author"] == "A"
    assert data["doc"]["pubdate"] == "Jan 1, 2020"
    assert data["doc"]["link"] == {"class": "x"}
    assert "title" not in data
    assert "author" not in data
    assert "pubdate" not in data
    assert "link" not in data

    md_data = yaml.load(md.read_text(encoding="utf-8").split("---\n", 2)[1])
    assert md_data["doc"]["title"] == "T"
    assert md_data["doc"]["author"] == "A"
    assert md_data["doc"]["pubdate"] == "Jan 1, 2020"
    assert md_data["doc"]["link"] == {"tracking": False}
    assert "title" not in md_data

    out_lines = capsys.readouterr().out.strip().splitlines()
    assert f"{yml}: migrated" in out_lines
    assert f"{md}: migrated" in out_lines
    assert "2 files checked" in out_lines[-2]
    assert "2 files changed" in out_lines[-1]
