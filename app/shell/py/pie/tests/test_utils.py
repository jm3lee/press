import json

from pie import utils


def test_write_json_roundtrip(tmp_path):
    data = {"name": "pie", "value": 42}
    path = tmp_path / "data.json"
    utils.write_json(data, str(path))
    assert utils.read_json(str(path)) == data


def test_write_utf8_roundtrip(tmp_path):
    text = "Hello π"
    path = tmp_path / "file.txt"
    utils.write_utf8(text, str(path))
    assert utils.read_utf8(str(path)) == text


def test_load_exclude_file_patterns(tmp_path):
    (tmp_path / "a.md").write_text("", encoding="utf-8")
    (tmp_path / "note.txt").write_text("", encoding="utf-8")
    (tmp_path / "error.log").write_text("", encoding="utf-8")
    cfg = tmp_path / "exclude.yml"
    cfg.write_text("- a.md\n- '*.txt'\n- 'regex:.*\\.log'\n", encoding="utf-8")
    exclude = utils.load_exclude_file(cfg, tmp_path)
    assert (tmp_path / "a.md") in exclude
    assert (tmp_path / "note.txt") in exclude
    assert (tmp_path / "error.log") in exclude
