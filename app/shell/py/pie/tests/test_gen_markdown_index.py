import subprocess
from pathlib import Path

# Path to the CLI script relative to this file
SCRIPT = Path(__file__).resolve().parents[5] / "app" / "shell" / "bin" / "gen-markdown-index"


def run_script(path: Path) -> str:
    result = subprocess.run(
        [str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def test_nested_directory_listing(tmp_path):
    (tmp_path / "a.yml").write_text("id: a\ntitle: Alpha\n")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "index.yml").write_text("id: sub\ntitle: Sub\n")
    (sub / "b.yml").write_text("id: b\ntitle: Beta\n")

    output = run_script(tmp_path)
    assert output.splitlines() == [
        "- {{a|linktitle}}",
        "- {{sub|linktitle}}",
        "  - {{b|linktitle}}",
    ]
