from __future__ import annotations

from pathlib import Path
import io
import yaml

from pie.update import metadata as update_metadata


def test_adds_metadata_from_file(tmp_path: Path, monkeypatch, capsys) -> None:
    """YAML from a file is merged into metadata."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("title: Test\n", encoding="utf-8")
    data_file = tmp_path / "add.yml"
    data_file.write_text("foo:\n  bar: a\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    update_metadata.main(["-f", str(data_file), "src/doc.yml"])

    assert yaml.safe_load(yml.read_text(encoding="utf-8")) == {
        "title": "Test",
        "foo": {"bar": "a"},
    }
    captured = capsys.readouterr()
    assert captured.out == ""
    log_text = (tmp_path / "log/update-metadata.txt").read_text(encoding="utf-8")
    assert "src/doc.yml updated" in log_text
    assert "Summary {'checked': 1, 'changed_count': 1}" in log_text


def test_reads_yaml_from_stdin(tmp_path: Path, monkeypatch, capsys) -> None:
    """Input is read from stdin when -f is not given."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("title: Test\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        update_metadata.sys, "stdin", io.StringIO("foo:\n  - a\n  - b\n")
    )
    update_metadata.main(["src/doc.yml"])

    assert yaml.safe_load(yml.read_text(encoding="utf-8")) == {
        "title": "Test",
        "foo": ["a", "b"],
    }
    captured = capsys.readouterr()
    assert captured.out == ""


def test_conflict_skips_file(tmp_path: Path, monkeypatch, capsys) -> None:
    """Conflicting keys result in a warning and no changes."""
    src = tmp_path / "src"
    src.mkdir()
    yml = src / "doc.yml"
    yml.write_text("foo: 1\n", encoding="utf-8")
    data_file = tmp_path / "add.yml"
    data_file.write_text("foo: 2\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    code = update_metadata.main(["-f", str(data_file), "src/doc.yml"])

    assert code == 1
    assert yaml.safe_load(yml.read_text(encoding="utf-8")) == {"foo": 1}
    captured = capsys.readouterr()
    assert captured.out == ""
    log_text = (tmp_path / "log/update-metadata.txt").read_text(encoding="utf-8")
    assert "Conflict merging metadata for src/doc.yml" in log_text
    assert "Summary {'checked': 1, 'changed_count': 0}" in log_text
