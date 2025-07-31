import pytest
from pie import render_jinja_template as render_template


def test_default_class():
    desc = {"citation": "foo", "url": "/f"}
    html = render_template.linktitle(desc)
    assert 'class="internal-link"' in html


def test_override_class():
    desc = {"citation": "foo", "url": "/f", "link": {"class": "external"}}
    html = render_template.linktitle(desc)
    assert 'class="external"' in html


def test_tracking_false_adds_attributes():
    desc = {"link": {"tracking": False}}
    opts = render_template.get_tracking_options(desc)
    assert opts == 'rel="noopener noreferrer" target="_blank"'


def test_tracking_true_returns_empty():
    desc = {"link": {"tracking": True}}
    opts = render_template.get_tracking_options(desc)
    assert opts == ""


def test_no_link_returns_empty():
    desc = {"citation": "foo"}
    opts = render_template.get_tracking_options(desc)
    assert opts == ""


def test_missing_tracking_interpreted_as_false():
    desc = {"link": {}}
    opts = render_template.get_tracking_options(desc)
    assert opts == 'rel="noopener noreferrer" target="_blank"'
