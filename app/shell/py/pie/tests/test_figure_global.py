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
