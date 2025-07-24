import json
from pie import gen_markdown_index


def test_main_outputs_markdown(tmp_path, capsys):
    index_file = tmp_path / "index.json"
    index_file.write_text(json.dumps({
        "guide": {"name": "Guide", "url": "/guide.html"},
        "intro": {"title": "Introduction", "url": "/intro.html"},
    }))

    gen_markdown_index.main([str(index_file)])
    out = capsys.readouterr().out.strip().splitlines()
    assert out == [
        "- [Guide](/guide.html)",
        "- [Introduction](/intro.html)",
    ]
