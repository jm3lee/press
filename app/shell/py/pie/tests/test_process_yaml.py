from __future__ import annotations

import pytest
import yaml

from pie import process_yaml


def test_parse_args_returns_paths() -> None:
    args = process_yaml.parse_args(["in.yml", "out.yml"])
    assert args.paths == ["in.yml", "out.yml"]


def test_main_writes_augmented_metadata(monkeypatch) -> None:
    data = {"title": "T"}

    def fake_read(path: str):
        assert path == "in.yml"
        return data

    def fake_generate(meta: dict, path: str):
        assert meta == data
        assert path == "in.yml"
        return {**meta, "id": "t"}

    written: dict[str, object] = {}

    def fake_write(meta: dict, path: str) -> None:
        written["meta"] = meta
        written["path"] = path

    monkeypatch.setattr(process_yaml.Path, "exists", lambda self: True)
    monkeypatch.setattr(process_yaml, "read_from_yaml", fake_read)
    monkeypatch.setattr(process_yaml, "generate_missing_metadata", fake_generate)
    monkeypatch.setattr(process_yaml, "write_yaml", fake_write)
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    process_yaml.main(["in.yml"])

    assert written["path"] == "in.yml"
    assert written["meta"]["id"] == "t"


def test_main_emojifies_text(monkeypatch) -> None:
    data = {"title": ":smile:"}

    def fake_read(path: str):
        return data

    def fake_generate(meta: dict, path: str):
        return meta

    written: dict[str, object] = {}

    def fake_write(meta: dict, path: str) -> None:
        written["meta"] = meta

    monkeypatch.setattr(process_yaml.Path, "exists", lambda self: True)
    monkeypatch.setattr(process_yaml, "read_from_yaml", fake_read)
    monkeypatch.setattr(process_yaml, "generate_missing_metadata", fake_generate)
    monkeypatch.setattr(process_yaml, "write_yaml", fake_write)
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    process_yaml.main(["in.yml"])

    assert written["meta"]["title"] == "😄"


def test_main_errors_on_missing_metadata(monkeypatch) -> None:
    monkeypatch.setattr(process_yaml.Path, "exists", lambda self: True)
    monkeypatch.setattr(process_yaml, "read_from_yaml", lambda path: None)
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)

    errors: list[str] = []
    monkeypatch.setattr(process_yaml.logger, "error", lambda msg, **k: errors.append(msg))

    with pytest.raises(SystemExit) as excinfo:
        process_yaml.main(["in.yml"])

    assert excinfo.value.code == 1
    assert errors == ["No metadata found"]


def test_main_errors_on_read_failure(monkeypatch) -> None:
    def bad_read(path: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(process_yaml.Path, "exists", lambda self: True)
    monkeypatch.setattr(process_yaml, "read_from_yaml", bad_read)
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)

    errors: list[str] = []
    monkeypatch.setattr(process_yaml.logger, "error", lambda msg, **k: errors.append(msg))

    with pytest.raises(SystemExit) as excinfo:
        process_yaml.main(["in.yml"])

    assert excinfo.value.code == 1
    assert errors == ["Failed to process YAML"]


def test_main_skips_write_when_unchanged(tmp_path, monkeypatch) -> None:
    path = tmp_path / "in.yml"
    content = yaml.safe_dump({"title": "T"}, allow_unicode=True, sort_keys=False)
    path.write_text(content, encoding="utf-8")

    monkeypatch.setattr(
        process_yaml, "generate_missing_metadata", lambda m, p: m
    )
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    called = {"write": False}

    def fake_write(meta: dict, p: str) -> None:
        called["write"] = True

    monkeypatch.setattr(process_yaml, "write_yaml", fake_write)

    process_yaml.main([str(path)])

    assert not called["write"]


def test_main_skips_write_when_text_diff(tmp_path, monkeypatch) -> None:
    path = tmp_path / "in.yml"
    path.write_text('title: "T"\n', encoding="utf-8")

    monkeypatch.setattr(
        process_yaml, "generate_missing_metadata", lambda m, p: m
    )
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    called = {"write": False}

    def fake_write(meta: dict, p: str) -> None:
        called["write"] = True

    monkeypatch.setattr(process_yaml, "write_yaml", fake_write)

    process_yaml.main([str(path)])

    assert not called["write"]


def test_main_creates_file_when_missing(tmp_path, monkeypatch) -> None:
    path = tmp_path / "out.yml"

    def bad_read(p: str):  # pragma: no cover - ensure not called
        raise AssertionError("should not read")

    monkeypatch.setattr(process_yaml, "read_from_yaml", bad_read)
    monkeypatch.setattr(
        process_yaml, "generate_missing_metadata", lambda m, p: {"id": "x"}
    )
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    written: dict[str, object] = {}

    def fake_write(meta: dict, p: str) -> None:
        written["meta"] = meta
        written["path"] = p

    monkeypatch.setattr(process_yaml, "write_yaml", fake_write)

    process_yaml.main([str(path)])

    assert written["path"] == str(path)
    assert written["meta"] == {"id": "x"}
