import json
from pie import gen_markdown_index


def test_generate_lines_sorted_and_icon():
    index = {
        "b": {"name": "Beta", "url": "/b"},
        "a": {"name": "Alpha", "url": "/a", "icon": "*"},
    }
    lines = gen_markdown_index.generate_lines(index)
    assert lines == ["- [* Alpha](/a)", "- [Beta](/b)"]


def test_main_outputs_lines(tmp_path, capsys):
    data = {
        "item": {"name": "Foo", "url": "/foo"}
    }
    path = tmp_path / "index.json"
    path.write_text(json.dumps(data))

    gen_markdown_index.main([str(path)])
    out = capsys.readouterr().out.strip()
    assert out == "- [Foo](/foo)"


def test_main_writes_log_file(tmp_path):
    data = {"item": {"name": "Foo", "url": "/foo"}}
    index_path = tmp_path / "index.json"
    log_path = tmp_path / "index.log"
    index_path.write_text(json.dumps(data))

    gen_markdown_index.main([str(index_path), "--log", str(log_path)])

    assert log_path.exists()
