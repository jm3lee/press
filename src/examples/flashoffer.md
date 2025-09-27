This example shows how to render Flashoffer call-to-action buttons with the
`pie.flashoffer` helpers.

Available helpers:

- `pie.flashoffer.primary_cta(text, href, extra_classes="", rel=None,
  target=None, **attrs)` renders the filled primary button.
- `pie.flashoffer.outline_cta(text, href, extra_classes="", rel=None,
  target=None, **attrs)` renders the outline secondary button.
- `pie.flashoffer.preview_card(card)` renders the Flashoffer preview card from
  a mapping that includes `image_url`, `alt_text`, `link_href`, and `caption`.
- `pie.flashoffer.footer(**kwargs)` renders the Flashoffer footer. Customize the
  visible text by overriding keyword arguments such as `left_prefix`,
  `site_name`, `rights_statement`, and `email_label`.

## Step-by-step instructions

1. Confirm your template already loads the Press Jinja globals. Templates under
   `src/templates/` receive the globals automatically.
2. Decide on the link destination for each CTA and whether it needs a `target`
   or `rel` attribute.
3. Call the helper inside your template using the examples below. You can pass
   extra keyword arguments to append custom HTML attributes (such as data
   tracking identifiers).

## Primary CTA

Use the primary helper for your most important action.

```jinja
{{ pie.flashoffer.primary_cta("Start your free trial", "/signup") }}
```

renders as:

{{ pie.flashoffer.primary_cta("Start your free trial", "/signup") }}

## Outline CTA

Pair the outline helper with the primary button to offer a secondary action.

```jinja
{{ pie.flashoffer.outline_cta("Talk to sales", "/contact") }}
```

renders as:

{{ pie.flashoffer.outline_cta("Talk to sales", "/contact") }}

## Customize attributes

You can combine helpers with additional classes and attributes to match your
layout or analytics requirements.

```jinja
{{ pie.flashoffer.outline_cta(
    "View partner pricing",
    "https://example.com/pricing",
    extra_classes="mt-3",
    rel="noopener",
    target="_blank",
    data_tracking_id="hero-secondary",
) }}
```

renders as:

{{ pie.flashoffer.outline_cta(
    "View partner pricing",
    "https://example.com/pricing",
    extra_classes="mt-3",
    rel="noopener",
    target="_blank",
    data_tracking_id="hero-secondary",
) }}

## Preview card

Combine the preview card with CTA helpers when a template needs to hide the
full image behind a tap target.

```jinja
{% set preview = {
    "image_url": "https://cdn.example.com/image.jpg",
    "alt_text": "Gallery preview",
    "link_href": "https://example.com/gallery",
    "caption": "Captured in natural light.",
} %}
{{ pie.flashoffer.preview_card(preview) }}
```
{% set preview = {
    "image_url": "https://seattlefigurestudio.sfo3.cdn.digitaloceanspaces.com/landing/favicon-48x48.png",
    "alt_text": "Seattle Figure Studio Favicon",
    "link_href": "https://seattlefigurestudio.com",
    "caption": "a cool place",
} %}
{{ pie.flashoffer.preview_card(preview) }}

## Footer

Use the footer helper to render the contact information block.

```jinja
{{ pie.flashoffer.footer(
    left_prefix="©&nbsp;",
    site_name="Seattle Figure Studio",
    site_href="https://seattlefigurestudio.com",
    rights_statement="All rights reserved.",
    email_label="brian@seattlefigurestudio.com",
) }}
```

renders as:

{{ pie.flashoffer.footer() }}
