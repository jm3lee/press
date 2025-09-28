import textwrap

import pytest
from markupsafe import Markup

from pie import flashoffer


@pytest.mark.parametrize(
    "helper,expected_class",
    [
        (flashoffer.primary_cta, "btn btn-primary btn-lg px-4"),
        (flashoffer.outline_cta, "btn btn-outline-light btn-lg px-4"),
        (flashoffer.preview_card, None),
    ],
)
def test_cta_renders_anchor_with_expected_classes(helper, expected_class):
    if helper is flashoffer.preview_card:
        html = helper(
            {
                "image_url": "https://cdn.example.com/preview.jpg",
                "alt_text": "Preview image",
                "link_href": "https://example.com/full",
                "caption": "A short caption",
            }
        )
    else:
        html = helper("Join", "/apply")
    assert isinstance(html, Markup)
    if helper is flashoffer.preview_card:
        assert html.startswith("<div class=\"col\">")
    else:
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
        "<a class=\"btn btn-primary btn-lg px-4 cta\" "
        'data_testid="hero-cta" '
        'href="/learn" '
        'rel="noopener" '
        'target="_blank"'
        ">Learn More</a>"
    )


def test_cta_escapes_text_and_attribute_values():
    html = flashoffer.primary_cta('Use "quote"', '/promo?ref="id"')
    assert html == Markup(
        "<a class=\"btn btn-primary btn-lg px-4\" "
        'href="/promo?ref=&quot;id&quot;"'
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


def test_hero_banner_uses_theme_background():
    html = flashoffer.hero_banner()
    expected_style = (
        'style="background: var('
        "--flashoffer-hero-background, "
        "radial-gradient(circle at 10% -10%, rgba(255, 92, 92, 0.18), "
        "transparent 45%), "
        "radial-gradient(circle at 110% 20%, rgba(34, 139, 230, 0.16), "
        "transparent 55%), "
        'var(--press-background, #090b10));"'
    )
    assert expected_style in html


def test_hero_banner_supports_optional_image():
    html = flashoffer.hero_banner(
        hero_image_url="https://cdn.example.com/hero.png",
        hero_image_alt='Hero "quote"',
        hero_image_kwargs={
            "data_tracking_id": "hero-visual",
            "extra_classes": "rounded-5",
            "loading": "eager",
        },
    )
    assert '<div class="hero-visual-wrapper mx-auto mb-4">' in html
    assert 'class="hero-visual img-fluid rounded-5"' in html
    assert 'src="https://cdn.example.com/hero.png"' in html
    assert 'alt="Hero &quot;quote&quot;"' in html
    assert 'data-tracking-id="hero-visual"' in html
    assert 'loading="eager"' in html


def test_preview_card_renders_expected_markup():
    html = flashoffer.preview_card(
        {
            "image_url": "https://cdn.example.com/image.jpg",
            "alt_text": "Hero image",
            "link_href": "https://example.com/gallery",
            "caption": "The caption",
        }
    )
    assert html == Markup(
        textwrap.dedent(
            """\
            <div class="col">
              <div class="card h-100 bg-dark border border-light-subtle shadow-sm">
                <div class="card-img-top bg-black d-flex align-items-center justify-content-center rounded-top overflow-hidden position-relative preview-card">
                  <img alt="Hero image" class="img-fluid w-100 h-auto preview-image" loading="lazy" src="https://cdn.example.com/image.jpg">
                  <div class="preview-overlay">
                    <div class="text-center px-3">
                      <p class="mb-2 fw-semibold">Tap to preview this image.</p>
                      <a class="btn btn-outline-light btn-sm preview-toggle" href="https://example.com/gallery" role="button">View image</a>
                    </div>
                  </div>
                </div>
                <div class="card-body">
                  <p class="card-text mb-0 text-white-50">The caption</p>
                </div>
              </div>
            </div>
            """
        ).strip()
    )


def test_preview_card_escapes_attribute_values_and_caption_text():
    html = flashoffer.preview_card(
        {
            "image_url": '/img?tag="x"',
            "alt_text": 'Alt "quote"',
            "link_href": '/preview?ref="full"',
            "caption": 'Use <em>markup</em>',
        }
    )
    assert html == Markup(
        textwrap.dedent(
            """\
            <div class="col">
              <div class="card h-100 bg-dark border border-light-subtle shadow-sm">
                <div class="card-img-top bg-black d-flex align-items-center justify-content-center rounded-top overflow-hidden position-relative preview-card">
                  <img alt="Alt &quot;quote&quot;" class="img-fluid w-100 h-auto preview-image" loading="lazy" src="/img?tag=&quot;x&quot;">
                  <div class="preview-overlay">
                    <div class="text-center px-3">
                      <p class="mb-2 fw-semibold">Tap to preview this image.</p>
                      <a class="btn btn-outline-light btn-sm preview-toggle" href="/preview?ref=&quot;full&quot;" role="button">View image</a>
                    </div>
                  </div>
                </div>
                <div class="card-body">
                  <p class="card-text mb-0 text-white-50">Use &lt;em&gt;markup&lt;/em&gt;</p>
                </div>
              </div>
            </div>
            """
        ).strip()
    )


def test_preview_card_preserves_markup_caption():
    html = flashoffer.preview_card(
        {
            "image_url": "image.jpg",
            "alt_text": "Alt",
            "link_href": "link",
            "caption": Markup("Line with <strong>markup</strong>"),
        }
    )
    assert "<strong>markup</strong>" in html


def test_preview_card_allows_custom_overlay_content():
    html = flashoffer.preview_card(
        {
            "image_url": "image.jpg",
            "alt_text": "Alt",
            "link_href": "link",
            "caption": "Caption",
        },
        overlay_text="Tap <em>gently</em> to reveal",
        overlay_button_text="Open <strong>preview</strong>",
    )
    assert "Tap &lt;em&gt;gently&lt;/em&gt; to reveal" in html
    assert "Open &lt;strong&gt;preview&lt;/strong&gt;" in html


def test_preview_card_preserves_markup_overlay_content():
    html = flashoffer.preview_card(
        {
            "image_url": "image.jpg",
            "alt_text": "Alt",
            "link_href": "link",
            "caption": "Caption",
        },
        overlay_text=Markup("Tap to reveal <em>now</em>"),
        overlay_button_text=Markup("<strong>Reveal</strong>"),
    )
    assert "Tap to reveal <em>now</em>" in html
    assert (
        '<a class="btn btn-outline-light btn-sm preview-toggle" '
        'href="link" role="button"><strong>Reveal</strong></a>'
    ) in html


@pytest.mark.parametrize("missing_key", ["image_url", "alt_text", "link_href", "caption"])
def test_preview_card_requires_expected_card_keys(missing_key):
    card = {
        "image_url": "image.jpg",
        "alt_text": "Alt",
        "link_href": "link",
        "caption": "Caption",
    }
    card.pop(missing_key)
    with pytest.raises(KeyError):
        flashoffer.preview_card(card)


def test_section_header_renders_all_fields_and_escapes_strings():
    html = flashoffer.section_header(
        eyebrow="Studio <mark>news</mark>",
        title="Fresh & inspiring",
        body_html="Browse <strong>stories</strong>",
    )
    assert html == Markup(
        textwrap.dedent(
            """\
            <div class="row justify-content-center mb-5 text-center">
              <div class="col-lg-8">
                <span class="eyebrow mb-3 d-inline-block text-white-50">Studio &lt;mark&gt;news&lt;/mark&gt;</span>
                <h2 class="fw-semibold mb-3">Fresh &amp; inspiring</h2>
                <p class="mb-0 text-white-50">Browse &lt;strong&gt;stories&lt;/strong&gt;</p>
              </div>
            </div>
            """
        ).strip()
    )


def test_section_header_omits_missing_parts_and_preserves_markup():
    html = flashoffer.section_header(title=Markup("Featured <em>Sessions</em>"))
    assert html == Markup(
        textwrap.dedent(
            """\
            <div class="row justify-content-center mb-5 text-center">
              <div class="col-lg-8">
                <h2 class="fw-semibold mb-3">Featured <em>Sessions</em></h2>
              </div>
            </div>
            """
        ).strip()
    )


def test_footer_renders_expected_markup():
    html = flashoffer.footer()
    assert html == Markup(
        textwrap.dedent(
            """\
            <footer class="container py-4 small" id="contact">
              <div class="row gy-3 align-items-center">
                <div class="col-12 col-md">©&nbsp;
                  <a class="link text-decoration-none" href="https://example.com/flashoffer">Flashoffer</a>. All rights reserved.
                </div>
                <div class="col-12 col-md-auto">
                  <a class="fw-semibold" href="mailto:support@example.com">support@example.com</a>
                </div>
              </div>
            </footer>
            """
        ).strip()
    )


def test_footer_allows_custom_text_and_markup():
    html = flashoffer.footer(
        container_id="footer",  # attribute, not displayed
        left_prefix=Markup("<strong>&copy;</strong>&nbsp;"),
        site_name=Markup("<em>Pie Corp</em>"),
        site_href="/about",
        rights_statement="All <rights>",
        email_label=Markup("<span>Contact&nbsp;Us</span>"),
        email_href="mailto:support@example.com",
    )
    assert "<em>Pie Corp</em>" in html
    assert "<span>Contact&nbsp;Us</span>" in html
    assert "All &lt;rights&gt;" in html
    assert "href=\"/about\"" in html
    assert "href=\"mailto:support@example.com\"" in html


def test_footer_escapes_plain_text_segments():
    html = flashoffer.footer(
        left_prefix='"copy" ',
        site_name='Pie & Co',
        rights_statement='Rights "reserved"',
        email_label='team@example.com?subject="Hi"',
        email_href='mailto:team@example.com?subject="Hi"',
    )
    assert '&#34;copy&#34;' in html
    assert 'Pie &amp; Co' in html
    assert 'Rights &#34;reserved&#34;' in html
    assert 'team@example.com?subject=&#34;Hi&#34;' in html


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

    cmarkgfm_stub = types.ModuleType("cmarkgfm")

    def _markdown_to_html(*args, **kwargs):  # pragma: no cover - stub
        return ""

    cmarkgfm_stub.github_flavored_markdown_to_html = _markdown_to_html
    monkeypatch.setitem(sys.modules, "cmarkgfm", cmarkgfm_stub)

    class _FakeLogger:
        def remove(self, *args, **kwargs):  # pragma: no cover - stub
            return None

        def add(self, *args, **kwargs):  # pragma: no cover - stub
            return 0

    loguru_stub = types.ModuleType("loguru")
    loguru_stub.logger = _FakeLogger()
    monkeypatch.setitem(sys.modules, "loguru", loguru_stub)

    ruamel_stub = types.ModuleType("ruamel")
    ruamel_yaml_stub = types.ModuleType("ruamel.yaml")

    class _FakeYAML:  # pragma: no cover - stub
        def __init__(self, *args, **kwargs):
            pass

    ruamel_yaml_stub.YAML = _FakeYAML
    ruamel_yaml_stub.YAMLError = Exception
    monkeypatch.setitem(sys.modules, "ruamel", ruamel_stub)
    monkeypatch.setitem(sys.modules, "ruamel.yaml", ruamel_yaml_stub)

    emoji_stub = types.ModuleType("emoji")

    def _emojize(value, *args, **kwargs):  # pragma: no cover - stub
        return value

    emoji_stub.emojize = _emojize
    monkeypatch.setitem(sys.modules, "emoji", emoji_stub)

    class _FakeTemplate:
        def render(self, *args, **kwargs):  # pragma: no cover - stub
            return ""

        @property
        def module(self):  # pragma: no cover - stub
            return types.SimpleNamespace(anchor=lambda _id: "")

    class _FakeEnvironment:
        def __init__(self, *args, **kwargs):  # pragma: no cover - stub
            self.globals = {}
            self.filters = {}

        def from_string(self, *args, **kwargs):  # pragma: no cover - stub
            return _FakeTemplate()

        def get_template(self, *args, **kwargs):  # pragma: no cover - stub
            return _FakeTemplate()

    class _FakeLoader:  # pragma: no cover - stub
        def __init__(self, *args, **kwargs):
            pass

    jinja2_stub = types.ModuleType("jinja2")
    jinja2_stub.Environment = _FakeEnvironment
    jinja2_stub.FileSystemLoader = _FakeLoader
    jinja2_stub.StrictUndefined = object
    jinja2_stub.TemplateNotFound = Exception
    jinja2_stub.TemplateSyntaxError = Exception
    monkeypatch.setitem(sys.modules, "jinja2", jinja2_stub)

    from pie.render import jinja

    flashoffer_global = jinja.env.globals["pie"]["flashoffer"]
    assert flashoffer_global.primary_cta is flashoffer.primary_cta
    assert flashoffer_global.outline_cta is flashoffer.outline_cta
    assert flashoffer_global.preview_card is flashoffer.preview_card
    assert flashoffer_global.footer is flashoffer.footer
