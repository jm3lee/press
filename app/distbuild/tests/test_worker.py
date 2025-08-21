import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "py"))
from distbuild.worker import execute_commands


def test_execute_commands_echo():
    results = execute_commands(["echo hello"])
    assert results[0]["returncode"] == 0
    assert "hello" in results[0]["stdout"].strip()
