# Codex Instructions for Flashoffer CTAs

The following block can be copied into an `AGENTS.md` file so Codex-powered
agents know how to render landing page buttons using `pie.flashoffer`.

```
# Flashoffer Helpers
- Use `pie.flashoffer.primary_cta(text, href, extra_classes="", rel=None,
  target=None, **attrs)` for the solid call-to-action button.
- Use `pie.flashoffer.outline_cta(text, href, extra_classes="", rel=None,
  target=None, **attrs)` for the outline button variant.
- Use `pie.flashoffer.hero_banner(...)` to render the Flashoffer hero banner.
  Configure the eyebrow, heading, description, and each call-to-action via the
  helper parameters or pass keyword argument dictionaries through to the CTA
  helpers.
- Use `pie.flashoffer.section_header(eyebrow=None, title=None, body_html=None)`
  to render centered section headers. Each argument may be omitted, plain text,
  or trusted `Markup` when inline HTML is required.
- Use `pie.flashoffer.preview_card(card, overlay_text="...",
  overlay_button_text="...")` to render the preview card markup. The `card`
  mapping must include `image_url`, `alt_text`, `link_href`, and `caption`
  keys. Override `overlay_text` and `overlay_button_text` to customise the
  overlay messaging while keeping HTML escaping intact. The defaults prompt
  visitors with "Tap to preview this image." and "View image".
- Use `pie.flashoffer.footer(...)` to render the Flashoffer footer snippet.
  All visible text segments are configurable through the helper arguments. The
  defaults render "Flashoffer" linked to `https://example.com/flashoffer` and
  the contact address `support@example.com`.
- Pass any additional keyword arguments to append raw HTML attributes (for
  example, `data_tracking_id="hero"`).
- Provide `rel` and `target` explicitly when linking to external destinations.
- The helpers escape text and attribute values automatically; wrap trusted
  markup in `markupsafe.Markup` if you need to opt out of escaping. The preview
  card preserves `Markup` captions while escaping plain text strings.
- Each helper builds HTML with the [`dominate`](https://github.com/Knio/
  dominate) DOM builder, so you can compose additional fragments by converting
  any returned `Markup` into `dominate.util.raw` when necessary.
```

## Hero banner parameters

`pie.flashoffer.hero_banner` renders the landing hero with an eyebrow, heading,
supporting copy, and up to three CTAs. The helper accepts:

- `eyebrow`, `title`, and `description` – either plain strings or trusted
  `Markup`. Use `Markup` when the layout needs inline emphasis, just as you
  would for preview captions in the
  [preview card example](../../src/examples/flashoffer.md#preview-card).
- `primary_cta_text` and `primary_cta_href` – populate the filled CTA. Extend
  or override button attributes with `primary_cta_kwargs`, which forwards keys
  like `extra_classes`, `rel`, and `target` to
  [`pie.flashoffer.primary_cta`](../../src/examples/flashoffer.md#primary-cta).
  The defaults link to `https://example.com/flashoffer` with the label
  "Explore Flashoffer components" so documentation mirrors demo copy.
- `first_outline_text`/`href` and `second_outline_text`/`href` – populate the
  outline CTAs. Each CTA also accepts a `*_kwargs` mapping. These dictionaries
  are passed straight into `pie.flashoffer.outline_cta`, so you can add
  tracking attributes or reuse the same label overrides that appear alongside
  the [preview card helper](../../src/examples/flashoffer.md#preview-card).
  Default copy references "Contact support" and "View documentation" to keep
  the hero aligned with footer contact details.
- `hero_image_url`, `hero_image_alt`, and `hero_image_kwargs` – optionally add a
  focal image below the body copy. Provide `hero_image_alt` for accessibility
  text and leverage `hero_image_kwargs` to append custom HTML attributes or
  override defaults such as the loading behaviour.

To hide a CTA entirely, supply a utility class through the corresponding
`*_kwargs`, for example `{"extra_classes": "d-none"}`. You can also reorder
buttons inside the responsive flex container by assigning Bootstrap order
classes (`order-2`, `order-3`, and so on) via the same dictionaries.

The hero container ships with a gradient background that mirrors the Press
theme. Override it by setting a custom `--flashoffer-hero-background` value in
your CSS when a landing page needs different art direction. You can also tweak
the default layout and color treatments by redefining the Flashoffer CSS custom
properties exposed in `src/css/style.css`. Variables such as
`--flashoffer-hero-padding-block`, `--flashoffer-hero-visual-shadow`, and
`--flashoffer-preview-overlay-background` provide override points without
requiring manual selector overrides.

## Section header parameters

`pie.flashoffer.section_header` renders a centered heading stack that mirrors
the Jinja macro used in Flashoffer templates. Supply any combination of
`eyebrow`, `title`, and `body_html` values to control which elements are shown.
When you pass plain strings they are escaped automatically; wrap inline HTML in
`markupsafe.Markup` to opt into trusted markup. The helper keeps the same
spacing, text alignment, and color treatments as the original macro so it can
drop into landing sections without extra CSS overrides.
