from pie.render import jinja as render_template


def test_figure_prefers_caption_metadata():
    desc = {
        "title": "Option Pricing & Greeks Calculator screenshot",
        "url": "https://koreanbriancom.sfo3.cdn.digitaloceanspaces.com/v2/files/0/VlYZ9h1q",
        "figure": {"caption": "Option Pricing & Greeks Calculator"},
    }
    expected = (
        "<figure><img src=\"https://koreanbriancom.sfo3.cdn.digitaloceanspaces.com/v2/files/0/VlYZ9h1q\" "
        "alt=\"Option Pricing & Greeks Calculator screenshot\" loading=\"lazy\"/>"
        "<figcaption>Option Pricing & Greeks Calculator</figcaption></figure>"
    )
    assert render_template.figure(desc) == expected


def test_figure_uses_title_when_caption_missing():
    desc = {
        "title": "Option Pricing & Greeks Calculator screenshot",
        "url": "https://koreanbriancom.sfo3.cdn.digitaloceanspaces.com/v2/files/0/VlYZ9h1q",
    }
    expected = (
        "<figure><img src=\"https://koreanbriancom.sfo3.cdn.digitaloceanspaces.com/v2/files/0/VlYZ9h1q\" "
        "alt=\"Option Pricing & Greeks Calculator screenshot\" loading=\"lazy\"/>"
        "<figcaption>Option Pricing & Greeks Calculator screenshot</figcaption></figure>"
    )
    assert render_template.figure(desc) == expected


def test_figure_generates_srcset_from_widths():
    desc = {
        "title": "Responsive image",
        "url": "/img/sample-400.jpg",
        "figure": {
            "caption": "Responsive",
            "pattern": "/img/sample-{width}.jpg",
            "widths": [400, 800],
            "sizes": "(max-width: 800px) 100vw, 800px",
        },
    }
    expected = (
        "<figure><img src=\"/img/sample-400.jpg\" "
        "srcset=\"/img/sample-400.jpg 400w, /img/sample-800.jpg 800w\" "
        "sizes=\"(max-width: 800px) 100vw, 800px\" alt=\"Responsive image\" "
        "loading=\"lazy\"/><figcaption>Responsive</figcaption></figure>"
    )
    assert render_template.figure(desc) == expected
