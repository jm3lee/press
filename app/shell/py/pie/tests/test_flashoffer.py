import pytest
from markupsafe import Markup

from pie import flashoffer


@pytest.mark.parametrize(
    "helper,expected_class",
    [
        (flashoffer.primary_cta, "btn btn-primary btn-lg px-4"),
        (flashoffer.outline_cta, "btn btn-outline-light btn-lg px-4"),
    ],
)
def test_cta_renders_anchor_with_expected_classes(helper, expected_class):
    html = helper("Join", "/apply")
    assert isinstance(html, Markup)
    assert html == Markup(
        f'<a class="{expected_class}" href="/apply">Join</a>'
    )


def test_cta_includes_optional_attributes_and_extra_kwargs():
    html = flashoffer.primary_cta(
        "Learn More",
        "/learn",
        extra_classes="cta",
        rel="noopener",
        target="_blank",
        data_testid="hero-cta",
    )
    assert html == Markup(
        "<a "
        'class="btn btn-primary btn-lg px-4 cta" '
        'href="/learn" '
        'rel="noopener" '
        'target="_blank" '
        'data_testid="hero-cta"'
        ">Learn More</a>"
    )


def test_cta_escapes_text_and_attribute_values():
    html = flashoffer.primary_cta('Use "quote"', '/promo?ref="id"')
    assert html == Markup(
        "<a "
        'class="btn btn-primary btn-lg px-4" '
        'href="/promo?ref=&#34;id&#34;"'
        ">Use &#34;quote&#34;</a>"
    )


def test_cta_preserves_markup_text():
    html = flashoffer.primary_cta(Markup("<strong>Ready</strong>"), "/go")
    assert html == Markup(
        "<a "
        'class="btn btn-primary btn-lg px-4" '
        'href="/go"'
        "><strong>Ready</strong></a>"
    )


def test_flashoffer_module_is_registered_with_jinja_globals(monkeypatch, tmp_path):
    import sys
    import types

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "macros.jinja").write_text(
        "{% macro anchor(id) %}<a id=\"{{ id }}\"></a>{% endmacro %}",
        encoding="utf-8",
    )
    monkeypatch.setenv("PIE_DATA_DIR", str(templates_dir))

    redis_stub = types.ModuleType("redis")

    class _FakeRedis:
        def __init__(self, *args, **kwargs):
            pass

    redis_stub.Redis = _FakeRedis
    monkeypatch.setitem(sys.modules, "redis", redis_stub)

    flatten_stub = types.ModuleType("flatten_dict")

    def _unflatten(*args, **kwargs):  # pragma: no cover - simple stub
        return {}

    flatten_stub.unflatten = _unflatten
    monkeypatch.setitem(sys.modules, "flatten_dict", flatten_stub)

    from pie.render import jinja

    flashoffer_global = jinja.env.globals["pie"]["flashoffer"]
    assert flashoffer_global.primary_cta is flashoffer.primary_cta
    assert flashoffer_global.outline_cta is flashoffer.outline_cta
