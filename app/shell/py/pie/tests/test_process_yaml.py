import pytest

from pie import process_yaml


def test_parse_args():
    args = process_yaml.parse_args(["in.yml", "out.yml"])
    assert args.input == "in.yml"
    assert args.output == "out.yml"
    assert args.log is None
    assert args.verbose is False


def test_main_writes_generated_metadata(monkeypatch):
    written = {}
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml, "read_from_yaml", lambda path: {"title": "T"})

    def fake_generate(data, path):
        data = dict(data)
        data["id"] = "t"
        return data

    monkeypatch.setattr(process_yaml, "generate_missing_metadata", fake_generate)
    monkeypatch.setattr(process_yaml, "write_yaml", lambda data, path: written.update({"data": data, "path": path}))
    debugs = []
    monkeypatch.setattr(process_yaml.logger, "debug", lambda msg, **kw: debugs.append((msg, kw)))
    monkeypatch.setattr(process_yaml.logger, "error", lambda *a, **k: None)
    process_yaml.main(["in.yml", "out.yml"])
    assert written == {"data": {"title": "T", "id": "t"}, "path": "out.yml"}
    assert debugs and debugs[0][1]["path"] == "out.yml"


def test_main_missing_metadata_exits(monkeypatch):
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(process_yaml, "read_from_yaml", lambda path: None)
    monkeypatch.setattr(process_yaml, "write_yaml", lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not write")))
    errors = []
    monkeypatch.setattr(process_yaml.logger, "error", lambda msg, **kw: errors.append((msg, kw)))
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)
    with pytest.raises(SystemExit) as exc:
        process_yaml.main(["in.yml", "out.yml"])
    assert exc.value.code == 1
    assert errors and errors[0][0] == "No metadata found"


def test_main_read_error_exits(monkeypatch):
    monkeypatch.setattr(process_yaml, "configure_logging", lambda *a, **k: None)

    def boom(path):
        raise ValueError("boom")

    monkeypatch.setattr(process_yaml, "read_from_yaml", boom)
    errors = []
    monkeypatch.setattr(process_yaml.logger, "error", lambda msg, **kw: errors.append((msg, kw)))
    monkeypatch.setattr(process_yaml.logger, "debug", lambda *a, **k: None)
    with pytest.raises(SystemExit) as exc:
        process_yaml.main(["in.yml", "out.yml"])
    assert exc.value.code == 1
    assert errors and errors[0][0] == "Failed to process YAML"
