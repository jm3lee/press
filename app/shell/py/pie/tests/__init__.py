import sys
import types
from pathlib import Path
import re

# Simple templating fallback used when jinja2 is unavailable
class _Template:
    _pattern = re.compile(r"{{([^{}]+)}}")

    def __init__(self, text: str):
        self.text = text

    def render(self, **ctx):
        def repl(m):
            expr = m.group(1)
            return str(eval(expr, {}, ctx))
        return self._pattern.sub(repl, self.text)

class _Env:
    def __init__(self):
        self.filters = {}
        self.globals = {}

    def from_string(self, text: str):
        return _Template(text)

    def get_template(self, name: str):
        return _Template(Path(name).read_text(encoding='utf-8'))

try:  # pragma: no cover - only used when jinja2 is missing
    import jinja2  # type: ignore[unused-import]
except ModuleNotFoundError:  # pragma: no cover - fallback for missing dep
    class _FSLoader:
        def __init__(self, _path: str):
            self.path = _path

    class _StrictUndefined:
        pass

    jinja2 = types.ModuleType("jinja2")
    jinja2.Environment = lambda *a, **k: _Env()
    jinja2.FileSystemLoader = _FSLoader
    jinja2.StrictUndefined = _StrictUndefined
    sys.modules["jinja2"] = jinja2
