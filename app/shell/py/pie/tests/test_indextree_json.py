from pathlib import Path

from pie.indextree_json import scan_dir


def test_scan_dir(tmp_path: Path) -> None:
    (tmp_path / "alpha").mkdir()
    (tmp_path / "alpha" / "beta.md").write_text("beta")
    (tmp_path / "gamma.md").write_text("gamma")

    tree = scan_dir(tmp_path, "/")
    assert tree == [
        {
            "id": "alpha",
            "title": "Alpha",
            "url": "/alpha",
            "children": [
                {"id": "beta", "title": "Beta", "url": "/alpha/beta"}
            ],
        },
        {"id": "gamma", "title": "Gamma", "url": "/gamma"},
    ]

