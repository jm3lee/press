from pie.gen_markdown_index import generate


def test_show_property(tmp_path):
    """Nodes with 'show: false' are skipped."""
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


def test_missing_id_uses_filename(tmp_path):
    """Files without an explicit id derive it from the filename."""
    (tmp_path / "foo.yml").write_text("name: Foo\ntitle: Foo\n")

    lines = list(generate(tmp_path))

    assert lines == ['- {{"foo"|linktitle}}']
