from __future__ import annotations

import pytest

from pie import process_yaml


def test_parse_args_returns_paths() -> None:
    args = process_yaml.parse_args(["in.yml", "out.yml"])
    assert args.input == "in.yml"
    assert args.output == "out.yml"


def test_main_writes_augmented_metadata(monkeypatch) -> None:
    data = {"title": "T"}

    def fake_read(path: str):
        assert path == "in.yml"
        return data

    def fake_generate(meta: dict, path: str):
        assert meta is data
        assert path == "in.yml"
        return {**meta, "id": "t"}

    written: dict[str, object] = {}

    def fake_write(meta: dict, path: str) -> None:
        written["meta"] = meta
        written["path"] = path

    monkeypatch.setattr(process_yaml, "read_from_yaml", fake_read)
    monkeypatch.setattr(process_yaml, "generate_missing_metadata", fake_generate)
    monkeypatch.setattr(process_yaml, "write_yaml", fake_write)
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    process_yaml.main(["in.yml", "out.yml"])

    assert written["path"] == "out.yml"
    assert written["meta"]["id"] == "t"


def test_main_errors_on_missing_metadata(monkeypatch) -> None:
    monkeypatch.setattr(process_yaml, "read_from_yaml", lambda path: None)
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)

    errors: list[str] = []
    monkeypatch.setattr(process_yaml.logger, "error", lambda msg, **k: errors.append(msg))

    with pytest.raises(SystemExit) as excinfo:
        process_yaml.main(["in.yml", "out.yml"])

    assert excinfo.value.code == 1
    assert errors == ["No metadata found"]


def test_main_errors_on_read_failure(monkeypatch) -> None:
    def bad_read(path: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(process_yaml, "read_from_yaml", bad_read)
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)

    errors: list[str] = []
    monkeypatch.setattr(process_yaml.logger, "error", lambda msg, **k: errors.append(msg))

    with pytest.raises(SystemExit) as excinfo:
        process_yaml.main(["in.yml", "out.yml"])

    assert excinfo.value.code == 1
    assert errors == ["Failed to process YAML"]
