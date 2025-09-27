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
