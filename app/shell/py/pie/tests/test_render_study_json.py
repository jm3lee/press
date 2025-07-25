import json
from pathlib import Path

from pie import render_study_json


def test_render_study_basic():
    index = {"item": {"title": "Foo"}}
    questions = [
        {"q": "Name {{item['title']}}", "c": ["A", "B"], "a": [0, "Because {{item['title']}}"]}
    ]
    rendered = render_study_json.render_study(index, questions)
    assert rendered == [{"q": "Name Foo", "c": ["A", "B"], "a": [0, "Because Foo"]}]


def test_main_outputs_stdout(tmp_path, capsys):
    index_file = tmp_path / "index.json"
    study_file = tmp_path / "study.json"
    index = {"val": {"title": "Bar"}}
    study = [{"q": "{{val['title']}}?", "c": ["X"], "a": [0, "{{val['title']}}"]}]
    index_file.write_text(json.dumps(index))
    study_file.write_text(json.dumps(study))

    render_study_json.main([str(index_file), str(study_file)])
    out = capsys.readouterr().out.strip()
    assert json.loads(out) == [{"q": "Bar?", "c": ["X"], "a": [0, "Bar"]}]


def test_main_writes_file(tmp_path):
    index_file = tmp_path / "index.json"
    study_file = tmp_path / "study.json"
    out_file = tmp_path / "out.json"
    index_file.write_text(json.dumps({"x": {"title": "Baz"}}))
    study_file.write_text(json.dumps([{"q": "{{x['title']}}", "c": ["Y"], "a": [0, ""]}]))

    render_study_json.main([str(index_file), str(study_file), "-o", str(out_file)])
    data = json.loads(out_file.read_text())
    assert data == [{"q": "Baz", "c": ["Y"], "a": [0, ""]}]
