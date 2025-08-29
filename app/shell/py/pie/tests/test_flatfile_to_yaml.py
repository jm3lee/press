from pie.flatfile_to_yaml import main
from pie.yaml import read_yaml


def test_flatfile_to_yaml(tmp_path):
    src = tmp_path / "data.ff"
    out = tmp_path / "out.yml"
    src.write_text("pie.answer\n{{ 3 + 4 }}\n", encoding="utf-8")
    main([str(src), str(out)])
    assert read_yaml(out) == {"pie": {"answer": "7"}}
