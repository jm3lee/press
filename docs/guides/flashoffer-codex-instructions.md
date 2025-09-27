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
- Use `pie.flashoffer.preview_card(card, overlay_text="...",
  overlay_button_text="...")` to render the preview card markup. The `card`
  mapping must include `image_url`, `alt_text`, `link_href`, and `caption`
  keys. Override `overlay_text` and `overlay_button_text` to customise the
  overlay messaging while keeping HTML escaping intact.
- Use `pie.flashoffer.footer(...)` to render the Flashoffer footer snippet.
  All visible text segments are configurable through the helper arguments.
- Pass any additional keyword arguments to append raw HTML attributes (for
  example, `data_tracking_id="hero"`).
- Provide `rel` and `target` explicitly when linking to external destinations.
- The helpers escape text and attribute values automatically; wrap trusted
  markup in `markupsafe.Markup` if you need to opt out of escaping. The preview
  card preserves `Markup` captions while escaping plain text strings.
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
  Link labels should align with the footer language described in the
  [Flashoffer footer](../../src/examples/flashoffer.md#footer) guidance.
- `first_outline_text`/`href` and `second_outline_text`/`href` – populate the
  outline CTAs. Each CTA also accepts a `*_kwargs` mapping. These dictionaries
  are passed straight into `pie.flashoffer.outline_cta`, so you can add
  tracking attributes or reuse the same label overrides that appear alongside
  the [preview card helper](../../src/examples/flashoffer.md#preview-card).

To hide a CTA entirely, supply a utility class through the corresponding
`*_kwargs`, for example `{"extra_classes": "d-none"}`. You can also reorder
buttons inside the responsive flex container by assigning Bootstrap order
classes (`order-2`, `order-3`, and so on) via the same dictionaries.

The hero container ships with a gradient background that mirrors the Press
theme. Override it by setting a custom `--flashoffer-hero-background` value in
your CSS when a landing page needs different art direction.
