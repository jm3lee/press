import json
from pie import gen_markdown_index


def test_generate_lines_sorted_and_icon():
    index = {
        "b": {"name": "Beta", "url": "/b"},
        "a": {
            "name": "Alpha",
            "url": "/a",
            "icon": "*",
            "link": {"tracking": False},
        },
    }
    lines = gen_markdown_index.generate_lines(index)
    expected_a = {
        "citation": "Alpha",
        "url": "/a",
        "icon": "*",
        "link": {"tracking": False},
    }
    expected_b = {
        "citation": "Beta",
        "url": "/b",
    }
    expected_lines = [
        "- {{ " + json.dumps(expected_a, ensure_ascii=False) + " | linktitle }}",
        "- {{ " + json.dumps(expected_b, ensure_ascii=False) + " | linktitle }}",
    ]
    # - {{ {"citation": "Alpha", "url": "/a", "icon": "*", "link": {"tracking": false}} | linktitle }}
    # - {{ {"citation": "Beta", "url": "/b"} | linktitle }}
    assert lines == expected_lines


def test_main_outputs_lines(tmp_path, capsys):
    data = {
        "item": {
            "name": "Foo",
            "url": "/foo",
            "link": {"tracking": False},
        }
    }
    path = tmp_path / "index.json"
    path.write_text(json.dumps(data))

    gen_markdown_index.main([str(path)])
    out = capsys.readouterr().out.strip()
    desc = {"citation": "Foo", "url": "/foo", "link": {"tracking": False}}
    expected = "- {{ " + json.dumps(desc, ensure_ascii=False) + " | linktitle }}"
    # - {{ {"citation": "Foo", "url": "/foo", "link": {"tracking": false}} | linktitle }}
    assert out == expected


def test_main_writes_log_file(tmp_path):
    data = {"item": {"name": "Foo", "url": "/foo"}}
    index_path = tmp_path / "index.json"
    log_path = tmp_path / "index.log"
    index_path.write_text(json.dumps(data))

    gen_markdown_index.main([str(index_path), "--log", str(log_path)])

    assert log_path.exists()


def test_generate_lines_nested_dirs():
    index = {
        "foo": {"name": "Foo", "url": "/jp/foo.html"},
        "a": {"name": "A", "url": "/jp/a/index.html"},
        "bar": {"name": "Bar", "url": "/jp/a/bar.html"},
    }
    lines = gen_markdown_index.generate_lines(index)
    foo = {"citation": "Foo", "url": "/jp/foo.html"}
    a = {"citation": "A", "url": "/jp/a/index.html"}
    bar = {"citation": "Bar", "url": "/jp/a/bar.html"}
    expected = [
        "- {{ " + json.dumps(a, ensure_ascii=False) + " | linktitle }}",
        "  - {{ " + json.dumps(bar, ensure_ascii=False) + " | linktitle }}",
        "- {{ " + json.dumps(foo, ensure_ascii=False) + " | linktitle }}",
    ]
    assert lines == expected

