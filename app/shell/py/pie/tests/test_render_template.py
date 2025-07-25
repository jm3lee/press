import pytest
from pie import render_template


def test_default_class():
    desc = {"citation": "foo", "url": "/f"}
    html = render_template.linktitle(desc)
    assert 'class="internal-link"' in html


def test_override_class():
    desc = {"citation": "foo", "url": "/f", "link": {"class": "external"}}
    html = render_template.linktitle(desc)
    assert 'class="external"' in html
