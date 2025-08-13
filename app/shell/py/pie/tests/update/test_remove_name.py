from __future__ import annotations

from pathlib import Path

from pie.update import remove_name


def test_removes_name_fields(tmp_path: Path, capsys) -> None:
    """The remove-name script strips name fields from metadata files."""
    src = tmp_path / "src"
    src.mkdir()

    yml = src / "doc.yml"
    yml.write_text("title: Test\nname: Old\n", encoding="utf-8")

    md = src / "doc.md"
    md.write_text("---\nname: Old\n---\nbody\n", encoding="utf-8")

    yaml_file = src / "doc.yaml"
    yaml_file.write_text("title: Test\nname: Old\n", encoding="utf-8")

    remove_name.main([str(src)])

    assert "name:" not in yml.read_text(encoding="utf-8")
    assert "name:" not in md.read_text(encoding="utf-8")
    assert "name:" not in yaml_file.read_text(encoding="utf-8")

    out_lines = capsys.readouterr().out.strip().splitlines()
    assert f"{yml}: Old" in out_lines
    assert f"{md}: Old" in out_lines
    assert f"{yaml_file}: Old" in out_lines
    assert "3 files checked" in out_lines
    assert "3 files changed" in out_lines

