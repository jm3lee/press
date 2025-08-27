from pie import yaml as pyaml


def test_write_yaml_roundtrip(tmp_path):
    data = {"name": "pie", "value": 42}
    path = tmp_path / "data.yml"
    pyaml.write_yaml(data, path)
    assert pyaml.read_yaml(path) == data
