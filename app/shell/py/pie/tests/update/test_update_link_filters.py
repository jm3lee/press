from pathlib import Path

import pytest

from pie.update import link_filters


def test_converts_basic_filters(tmp_path: Path) -> None:
    fp = tmp_path / "example.md"
    fp.write_text('{{ hull | link }}\n', encoding="utf-8")
    assert link_filters.process_file(fp)
    assert fp.read_text(encoding="utf-8") == "{{ link('hull') }}\n"


def test_preserves_arguments(tmp_path: Path) -> None:
    fp = tmp_path / "example.md"
    fp.write_text('{{ hull|link(style="title") }}', encoding="utf-8")
    link_filters.process_file(fp)
    assert (
        fp.read_text(encoding="utf-8")
        == """{{ link('hull', style="title") }}"""
    )


def test_iter_files(tmp_path: Path) -> None:
    file1 = tmp_path / "one.txt"
    file1.write_text("", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    file2 = sub / "two.txt"
    file2.write_text("", encoding="utf-8")
    files = list(link_filters.iter_files([file1, sub]))
    assert set(files) == {file1, file2}


def test_process_file_handles_errors_and_no_changes(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"
    assert not link_filters.process_file(missing)
    fp = tmp_path / "plain.md"
    fp.write_text("no filters", encoding="utf-8")
    assert not link_filters.process_file(fp)
    assert fp.read_text(encoding="utf-8") == "no filters"


def test_parse_args_defaults() -> None:
    args = link_filters.parse_args(["file.txt"])
    assert args.paths == ["file.txt"]
    assert args.log == "log/update-link-filters.txt"


def test_main_changes_files(tmp_path: Path, capsys: "pytest.CaptureFixture[str]") -> None:
    fp1 = tmp_path / "a.md"
    fp1.write_text('{{ hull | link }}', encoding="utf-8")
    fp2 = tmp_path / "b.md"
    fp2.write_text("nothing here", encoding="utf-8")
    log_file = tmp_path / "log.txt"
    ret = link_filters.main([str(fp1), str(fp2), "--log", str(log_file)])
    assert ret == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert str(fp1) in out[0]
    assert "2 files checked" in out[-2]
    assert "1 file changed" in out[-1]
    assert fp1.read_text(encoding="utf-8") == "{{ link('hull') }}"
    assert fp2.read_text(encoding="utf-8") == "nothing here"
