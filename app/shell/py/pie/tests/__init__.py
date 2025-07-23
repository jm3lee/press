import sys
import json
import types
from pathlib import Path
from unittest.mock import Mock
import re

# Provide minimal fallbacks for optional dependencies so test collection works
if 'xmera' not in sys.modules:
    xmera = types.ModuleType('xmera')
    xmera.logger = Mock()
    utils = types.ModuleType('xmera.utils')
    utils.read_json = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    utils.read_utf8 = lambda p: Path(p).read_text(encoding='utf-8')
    xmera.utils = utils
    sys.modules['xmera'] = xmera
    sys.modules['xmera.utils'] = utils
    sys.modules['xmera.logger'] = xmera.logger

if 'yaml' not in sys.modules:
    yaml = types.ModuleType('yaml')
    yaml.safe_load = lambda c: json.loads(c if isinstance(c, str) else c.read())
    yaml.YAMLError = Exception
    sys.modules['yaml'] = yaml

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

if 'jinja2' not in sys.modules:
    class _FSLoader:
        def __init__(self, _path: str):
            self.path = _path

    class _StrictUndefined:
        pass

    jinja2 = types.ModuleType('jinja2')
    jinja2.Environment = lambda *a, **k: _Env()
    jinja2.FileSystemLoader = _FSLoader
    jinja2.StrictUndefined = _StrictUndefined
    sys.modules['jinja2'] = jinja2
