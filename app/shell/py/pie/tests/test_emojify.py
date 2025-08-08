import sys

from pie import emojify


def test_emojify_replaces_aliases(capsys):
    emojify.main(["Hello", ":smile:"])
    out = capsys.readouterr().out
    assert out.strip() == "Hello 😄"


def test_emojify_reads_stdin(capsys, monkeypatch):
    import io
    monkeypatch.setattr(sys, "stdin", io.StringIO("Good :dog:\n"))
    emojify.main([])
    out = capsys.readouterr().out
    assert out == "Good 🐶\n"
