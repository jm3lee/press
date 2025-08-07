from pie.gen_markdown_index import generate


def test_show_property(tmp_path):
    (tmp_path / "alpha.yml").write_text("id: alpha\ntitle: Alpha\n")
    (tmp_path / "beta.yml").write_text(
        "id: beta\ntitle: Beta\n" "gen-markdown-index:\n  show: false\n",
    )
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    (hidden / "index.yml").write_text(
        "id: hidden\ntitle: Hidden\n" "gen-markdown-index:\n  show: false\n",
    )
    (hidden / "child.yml").write_text("id: child\ntitle: Child\n")

    lines = list(generate(tmp_path))
    assert lines == [
        '- {{"alpha"|linktitle}}',
        '- {{"child"|linktitle}}',
    ]
