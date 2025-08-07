import os
import yaml
from pie import process_yaml


def test_main_generates_metadata(tmp_path):
    """item.yml -> metadata with url/citation/id."""
    src = tmp_path / "src"
    src.mkdir()
    inp = src / "item.yml"
    inp.write_text("{\"name\": \"Foo\"}")
    out = tmp_path / "out.yml"
    os.chdir(tmp_path)
    try:
        process_yaml.main([str(inp.relative_to(tmp_path)), str(out.relative_to(tmp_path))])
    finally:
        os.chdir("/tmp")

    data = yaml.safe_load(out.read_text())
    assert data["name"] == "Foo"
    assert data["url"] == "/item.html"
    assert data["citation"] == "foo"
    assert data["id"] == "item"


def test_main_writes_log_file(tmp_path):
    """CLI writes processed YAML and log."""
    src = tmp_path / "src"
    src.mkdir()
    inp = src / "doc.yml"
    inp.write_text("{\"name\": \"Foo\"}")
    out = tmp_path / "out.yml"
    log = tmp_path / "proc.log"
    os.chdir(tmp_path)
    try:
        process_yaml.main([
            str(inp.relative_to(tmp_path)),
            str(out.relative_to(tmp_path)),
            "--log",
            str(log.relative_to(tmp_path)),
        ])
    finally:
        os.chdir("/tmp")

    assert log.exists()
