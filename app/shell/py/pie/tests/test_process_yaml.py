from __future__ import annotations

import pytest
from io import StringIO

from ruamel.yaml import YAML

yaml = YAML(typ="safe")
yaml.allow_unicode = True
yaml.sort_keys = False
yaml.default_flow_style = False

from pie import process_yaml


def test_parse_args_returns_paths() -> None:
    args = process_yaml.parse_args(["in.yml", "out.yml"])
    assert args.paths == ["in.yml", "out.yml"]


def test_main_writes_augmented_metadata(tmp_path, monkeypatch) -> None:
    path = tmp_path / "in.yml"
    path.write_text("title: T\n", encoding="utf-8")

    def fake_generate(meta: dict, p: str):
        assert meta == {"title": "T"}
        assert p == str(path)
        return {**meta, "id": "t"}

    monkeypatch.setattr(process_yaml, "generate_missing_metadata", fake_generate)
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    process_yaml.main([str(path)])
    data = yaml.load(path.read_text(encoding="utf-8"))
    assert data["id"] == "t"


def test_main_emojifies_text(tmp_path, monkeypatch) -> None:
    path = tmp_path / "in.yml"
    path.write_text('title: ":smile:"\n', encoding="utf-8")

    monkeypatch.setattr(
        process_yaml, "generate_missing_metadata", lambda m, p: m
    )
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    process_yaml.main([str(path)])
    data = yaml.load(path.read_text(encoding="utf-8"))
    assert data["title"] == "😄"


def test_main_renders_jinja(tmp_path, monkeypatch) -> None:
    path = tmp_path / "jinja.yml"
    path.write_text("title: {{ 1 + 1 }}\n", encoding="utf-8")

    monkeypatch.setattr(
        process_yaml, "generate_missing_metadata", lambda m, p: m
    )
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    process_yaml.main([str(path)])
    assert path.read_text(encoding="utf-8").strip() == "title: 2"


def test_main_renders_jinja_recursively(tmp_path, monkeypatch) -> None:
    path = tmp_path / "jinja-nested.yml"
    path.write_text('title: "{{ \"{{ 1 + 1 }}\" }}"\n', encoding="utf-8")

    monkeypatch.setattr(
        process_yaml, "generate_missing_metadata", lambda m, p: m
    )
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)

    process_yaml.main([str(path)])
    assert path.read_text(encoding="utf-8").strip() == "title: 2"


def test_main_errors_on_missing_metadata(tmp_path, monkeypatch) -> None:
    path = tmp_path / "in.yml"
    path.write_text("", encoding="utf-8")

    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)

    errors: list[str] = []
    monkeypatch.setattr(process_yaml.logger, "error", lambda msg, **k: errors.append(msg))

    with pytest.raises(SystemExit) as excinfo:
        process_yaml.main([str(path)])

    assert excinfo.value.code == 1
    assert errors == ["No metadata found"]


def test_main_errors_on_read_failure(tmp_path, monkeypatch) -> None:
    path = tmp_path / "in.yml"
    path.write_text("title: T\n", encoding="utf-8")

    def boom(_text: str) -> str:
        raise RuntimeError("boom")

    monkeypatch.setattr(process_yaml.render_jinja, "render_jinja", boom)
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)

    errors: list[str] = []
    monkeypatch.setattr(process_yaml.logger, "error", lambda msg, **k: errors.append(msg))

    with pytest.raises(SystemExit) as excinfo:
        process_yaml.main([str(path)])

    assert excinfo.value.code == 1
    assert errors == ["Failed to process YAML"]


def test_main_skips_write_when_unchanged(tmp_path, monkeypatch) -> None:
    path = tmp_path / "in.yml"
    buf = StringIO()
    yaml.dump({"title": "T"}, buf)
    content = buf.getvalue()
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
