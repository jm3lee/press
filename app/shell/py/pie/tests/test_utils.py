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
