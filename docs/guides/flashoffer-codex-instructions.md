# Codex Instructions for Flashoffer CTAs

The following block can be copied into an `AGENTS.md` file so Codex-powered
agents know how to render landing page buttons using `pie.flashoffer`.

```
# Flashoffer CTA Helpers
- Use `pie.flashoffer.primary_cta(text, href, extra_classes="", rel=None,
  target=None, **attrs)` for the solid call-to-action button.
- Use `pie.flashoffer.outline_cta(text, href, extra_classes="", rel=None,
  target=None, **attrs)` for the outline button variant.
- Pass any additional keyword arguments to append raw HTML attributes (for
  example, `data_tracking_id="hero"`).
- Provide `rel` and `target` explicitly when linking to external destinations.
- The helpers escape text and attribute values automatically; wrap trusted
  markup in `markupsafe.Markup` if you need to opt out of escaping.
```
