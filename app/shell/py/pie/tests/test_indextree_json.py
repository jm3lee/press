from pathlib import Path

from pie.indextree_json import scan_dir


def test_scan_dir_uses_metadata(tmp_path: Path) -> None:
    root = tmp_path / "src"
    (root / "alpha").mkdir(parents=True)
    (root / "alpha" / "index.yml").write_text(
        "id: alpha-sec\ntitle: Alpha Section\nurl: /alpha/index.html\n",
        encoding="utf-8",
    )
    (root / "alpha" / "beta.yml").write_text(
        "id: beta-doc\ntitle: Beta Doc\nurl: /alpha/beta.html\n",
        encoding="utf-8",
    )
    (root / "gamma.yml").write_text(
        "id: gamma-doc\ntitle: Gamma Doc\nurl: /gamma.html\n"
        "gen-markdown-index:\n  link: false\n",
        encoding="utf-8",
    )

    tree = scan_dir(root)
    assert tree == [
        {
            "id": "alpha-sec",
            "label": "Alpha Section",
            "url": "/alpha/index.html",
            "children": [
                {
                    "id": "beta-doc",
                    "label": "Beta Doc",
                    "url": "/alpha/beta.html",
                }
            ],
        },
        {"id": "gamma-doc", "label": "Gamma Doc"},
    ]


def test_scan_dir_sorts_by_title(tmp_path: Path) -> None:
    root = tmp_path / "src"
    root.mkdir()

    # File names intentionally do not match title order
    (root / "b.yml").write_text(
        "id: a-doc\ntitle: A Doc\nurl: /custom/b.html\n",
        encoding="utf-8",
    )
    (root / "a.yml").write_text(
        "id: z-doc\ntitle: Z Doc\nurl: /custom/a.html\n",
        encoding="utf-8",
    )

    tree = scan_dir(root)
    assert tree == [
        {"id": "a-doc", "label": "A Doc", "url": "/custom/b.html"},
        {"id": "z-doc", "label": "Z Doc", "url": "/custom/a.html"},
    ]

