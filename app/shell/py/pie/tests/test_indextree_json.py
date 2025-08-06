from pathlib import Path
import os

from pie.indextree_json import scan_dir


def test_scan_dir_uses_metadata(tmp_path: Path) -> None:
    root = tmp_path / "src"
    (root / "alpha").mkdir(parents=True)

    (root / "alpha" / "index.yml").write_text(
        "title: Alpha Section\nname: Alpha Section\nid: alpha-sec\n", encoding="utf-8"
    )

    (root / "alpha" / "beta.md").write_text(
        "---\n"
        "title: Beta Doc\n"
        "id: beta-doc\n"
        "---\n"
        "beta\n",
        encoding="utf-8",
    )

    (root / "gamma.md").write_text(
        "---\n"
        "title: Gamma Doc\n"
        "id: gamma-doc\n"
        "---\n"
        "gamma\n",
        encoding="utf-8",
    )

    (root / "delta.md").write_text("delta\n", encoding="utf-8")

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        tree = scan_dir(Path("src"), "/")
    finally:
        os.chdir(cwd)
    assert tree == [
        {
            "id": "alpha-sec",
            "title": "Alpha Section",
            "url": "/alpha/index.html",
            "children": [
                {
                    "id": "beta-doc",
                    "title": "Beta Doc",
                    "url": "/alpha/beta.html",
                }
            ],
        },
        {"id": "gamma-doc", "title": "Gamma Doc", "url": "/gamma.html"},
    ]

