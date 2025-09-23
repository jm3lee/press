from pathlib import Path

from pie.update import breadcrumbs as update_breadcrumbs
from pie.yaml import write_yaml, yaml


def _read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---\n")
    if len(parts) < 3:
        return {}
    return yaml.load(parts[1]) or {}


def test_adds_frontmatter_breadcrumbs(tmp_path: Path, monkeypatch) -> None:
    """Markdown files gain breadcrumbs derived from their path."""

    src = tmp_path / "src" / "guides"
    src.mkdir(parents=True)
    md = src / "intro.md"
    md.write_text("---\ntitle: Intro\n---\nbody\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    update_breadcrumbs.main(["src"])

    frontmatter = _read_frontmatter(md)
    breadcrumbs = frontmatter["doc"]["breadcrumbs"]
    assert breadcrumbs == [
        {"title": "Home", "url": "/"},
        {"title": "Guides", "url": "/guides/"},
        {"title": "Intro"},
    ]


def test_updates_yaml_breadcrumbs(tmp_path: Path, monkeypatch) -> None:
    """Existing breadcrumbs are expanded to match the file structure."""

    src = tmp_path / "src" / "examples"
    src.mkdir(parents=True)
    yml = src / "demo.yml"
    yml.write_text(
        "doc:\n  breadcrumbs:\n  - title: Home\n    url: /\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    update_breadcrumbs.main(["src"])

    data = yaml.load(yml.read_text(encoding="utf-8"))
    breadcrumbs = data["doc"]["breadcrumbs"]
    assert breadcrumbs == [
        {"title": "Home", "url": "/"},
        {"title": "Examples", "url": "/examples/"},
        {"title": "Demo"},
    ]


def test_preserves_custom_titles(tmp_path: Path, monkeypatch) -> None:
    """Breadcrumb titles remain unchanged while URLs are corrected."""

    src = tmp_path / "src" / "examples"
    src.mkdir(parents=True)
    yml = src / "demo.yml"
    yml.write_text(
        "doc:\n"
        "  breadcrumbs:\n"
        "  - title: Home\n"
        "  - title: Custom Examples\n"
        "    url: /wrong/\n"
        "  - title: Demo Page\n"
        "    url: /wrong/demo/\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    update_breadcrumbs.main(["src"])

    data = yaml.load(yml.read_text(encoding="utf-8"))
    breadcrumbs = data["doc"]["breadcrumbs"]
    assert breadcrumbs == [
        {"title": "Home", "url": "/"},
        {"title": "Custom Examples", "url": "/examples/"},
        {"title": "Demo Page"},
    ]


def test_iter_metadata_skips_non_files_and_duplicates(tmp_path: Path, monkeypatch) -> None:
    """Directories and duplicate stems are ignored when scanning files."""

    root = tmp_path / "docs"
    root.mkdir()
    (root / "subdir.md").mkdir()
    first = root / "example.md"
    first.write_text("", encoding="utf-8")
    duplicate = root / "example.yaml"
    duplicate.write_text("", encoding="utf-8")

    collected: list[Path] = []

    def fake_loader(path: Path) -> dict:
        collected.append(path)
        return {"path": str(path)}

    monkeypatch.setattr(update_breadcrumbs, "load_metadata_pair", fake_loader)

    results = list(update_breadcrumbs._iter_metadata_files(root))

    assert len(results) == 1
    base, path, metadata = results[0]
    assert base == first.with_suffix("")
    assert path == first
    assert metadata == {"path": str(first)}
    assert collected == [first]


def test_normalise_breadcrumbs_filters_invalid_entries() -> None:
    """Only dictionaries with string titles are preserved."""

    data = [
        "not-a-dict",
        {"title": 42, "url": "/bad/"},
        {"title": "No Url", "url": ""},
        {"title": "Valid", "url": "/valid/"},
    ]

    assert update_breadcrumbs._normalise_breadcrumbs(data) == [
        {"title": "No Url"},
        {"title": "Valid", "url": "/valid/"},
    ]


def test_expected_breadcrumbs_handles_unrelated_paths() -> None:
    """Absolute roots that are unrelated to the base fall back to parts()."""

    base = Path("docs/guide")
    root = Path("/outside")

    result = update_breadcrumbs._expected_breadcrumbs(base, root, [])

    assert result == [
        {"title": "Home", "url": "/"},
        {"title": "Docs", "url": "/docs/"},
        {"title": "Guide"},
    ]


def test_write_yaml_breadcrumbs_no_changes(tmp_path: Path) -> None:
    """Returning ``False`` indicates YAML content already matches."""

    fp = tmp_path / "page.yml"
    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Docs", "url": "/docs/"},
        {"title": "Page"},
    ]

    write_yaml({"doc": {"breadcrumbs": breadcrumbs}}, fp)

    original = fp.read_text(encoding="utf-8")
    changed = update_breadcrumbs._write_yaml_breadcrumbs(fp, breadcrumbs, sort_keys=False)

    assert changed is False
    assert fp.read_text(encoding="utf-8") == original


def test_write_markdown_breadcrumbs_creates_frontmatter(tmp_path: Path) -> None:
    """Breadcrumbs are injected when Markdown lacks frontmatter."""

    fp = tmp_path / "note.md"
    fp.write_text("Body text\n", encoding="utf-8")
    breadcrumbs = [{"title": "Home", "url": "/"}, {"title": "Note"}]

    changed = update_breadcrumbs._write_markdown_breadcrumbs(fp, breadcrumbs, sort_keys=True)

    assert changed is True
    frontmatter = _read_frontmatter(fp)
    assert frontmatter["doc"]["breadcrumbs"] == breadcrumbs


def test_write_markdown_breadcrumbs_missing_end_returns_false(tmp_path: Path) -> None:
    """Malformed frontmatter leaves the file untouched."""

    fp = tmp_path / "broken.md"
    fp.write_text("---\ntitle: Broken\nbody\n", encoding="utf-8")
    breadcrumbs = [{"title": "Home", "url": "/"}, {"title": "Broken"}]

    changed = update_breadcrumbs._write_markdown_breadcrumbs(fp, breadcrumbs, sort_keys=False)

    assert changed is False
    assert fp.read_text(encoding="utf-8").startswith("---\ntitle: Broken")


def test_write_markdown_breadcrumbs_no_changes(tmp_path: Path) -> None:
    """Existing breadcrumbs prevent unnecessary updates."""

    fp = tmp_path / "page.md"
    breadcrumbs = [{"title": "Home", "url": "/"}, {"title": "Page"}]
    fp.write_text(
        "---\n"
        "doc:\n"
        "  breadcrumbs:\n"
        "  - title: Home\n"
        "    url: /\n"
        "  - title: Page\n"
        "---\n"
        "Body\n",
        encoding="utf-8",
    )

    changed = update_breadcrumbs._write_markdown_breadcrumbs(fp, breadcrumbs, sort_keys=False)

    assert changed is False


def test_write_breadcrumbs_unknown_suffix(tmp_path: Path) -> None:
    """Unsupported file extensions are ignored."""

    fp = tmp_path / "note.txt"
    fp.write_text("content", encoding="utf-8")

    changed = update_breadcrumbs._write_breadcrumbs(fp, [], sort_keys=False)

    assert changed is False


def test_update_directory_handles_various_paths(tmp_path: Path, monkeypatch) -> None:
    """Mixed metadata records update the appropriate files."""

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)

    outside_file = tmp_path / "outside.yml"
    outside_file.write_text("doc: {}\n", encoding="utf-8")

    expected_same = update_breadcrumbs._expected_breadcrumbs(
        Path("src/guides/intro"), Path("src"), []
    )

    def fake_iter(_: Path):
        yield Path("src/skip"), Path("src/skip.md"), None
        yield Path("src/guides/intro"), Path("src/guides/intro.md"), {"doc": {"breadcrumbs": expected_same}}
        yield Path("src/examples/advanced"), Path("src/examples/advanced.md"), {
            "doc": {"breadcrumbs": [{"title": "Home", "url": "/"}]},
            "path": ["missing.yml", str(outside_file)],
        }

    monkeypatch.setattr(update_breadcrumbs, "_iter_metadata_files", fake_iter)

    written: list[Path] = []

    def fake_write(fp: Path, breadcrumbs: list[dict[str, str]], sort_keys: bool) -> bool:
        written.append(fp)
        return fp == outside_file

    monkeypatch.setattr(update_breadcrumbs, "_write_breadcrumbs", fake_write)

    messages, checked = update_breadcrumbs.update_directory(Path("src"), sort_keys=True)

    assert checked == 1
    assert written == [outside_file]
    assert messages == [f"{outside_file}: breadcrumbs updated"]


def test_main_missing_directory(tmp_path: Path, monkeypatch) -> None:
    """Providing an invalid directory path exits with status 1."""

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)
    monkeypatch.setattr(update_breadcrumbs, "configure_logging", lambda verbose, log: None)

    assert update_breadcrumbs.main(["missing"]) == 1


def test_main_rejects_absolute_path_outside_workspace(tmp_path: Path, monkeypatch) -> None:
    """Absolute paths beyond the workspace boundary are rejected."""

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)
    monkeypatch.setattr(update_breadcrumbs, "configure_logging", lambda verbose, log: None)

    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    assert update_breadcrumbs.main([str(outside_dir)]) == 1
