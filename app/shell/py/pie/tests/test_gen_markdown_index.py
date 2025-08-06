from pathlib import Path
import subprocess

SCRIPT = Path(__file__).resolve().parents[3] / "bin" / "gen-markdown-index"


def test_show_property(tmp_path):
    (tmp_path / "alpha.yml").write_text("id: alpha\ntitle: Alpha\n")
    (tmp_path / "beta.yml").write_text(
        "id: beta\ntitle: Beta\n" "gen-markdown-index:\n  show: false\n"
    )
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    (hidden / "index.yml").write_text(
        "id: hidden\ntitle: Hidden\n" "gen-markdown-index:\n  show: false\n"
    )
    (hidden / "child.yml").write_text("id: child\ntitle: Child\n")

    result = subprocess.run(
        [str(SCRIPT), str(tmp_path)], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip().splitlines() == [
        '- {{"alpha"|linktitle}}',
        '- {{"child"|linktitle}}',
    ]

