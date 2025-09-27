This example shows how to render Flashoffer call-to-action buttons with the
`pie.flashoffer` helpers.

Available helpers:

- `pie.flashoffer.primary_cta(text, href, extra_classes="", rel=None,
  target=None, **attrs)` renders the filled primary button.
- `pie.flashoffer.outline_cta(text, href, extra_classes="", rel=None,
  target=None, **attrs)` renders the outline secondary button.

## Step-by-step instructions

1. Confirm your template already loads the Press Jinja globals. Templates under
   `src/templates/` receive the globals automatically.
2. Decide on the link destination for each CTA and whether it needs a `target`
   or `rel` attribute.
3. Call the helper inside your template using the examples below. You can pass
   extra keyword arguments to append custom HTML attributes (such as data
   tracking identifiers).

The rendered previews sit on a dark background so the outline style stays easy
to see.

## Primary CTA

Use the primary helper for your most important action.

```jinja
{{ pie.flashoffer.primary_cta("Start your free trial", "/signup") }}
```

renders as:

<div class="bg-dark p-4 rounded-3 d-inline-flex">
  {{ pie.flashoffer.primary_cta("Start your free trial", "/signup") }}
</div>

## Outline CTA

Pair the outline helper with the primary button to offer a secondary action.

```jinja
{{ pie.flashoffer.outline_cta("Talk to sales", "/contact") }}
```

renders as:

<div class="bg-dark p-4 rounded-3 d-inline-flex gap-3">
  {{ pie.flashoffer.primary_cta("Start your free trial", "/signup") }}
  {{ pie.flashoffer.outline_cta("Talk to sales", "/contact") }}
</div>

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

<div class="bg-dark p-4 rounded-3">
  {{ pie.flashoffer.outline_cta(
      "View partner pricing",
      "https://example.com/pricing",
      extra_classes="mt-3",
      rel="noopener",
      target="_blank",
      data_tracking_id="hero-secondary",
  ) }}
</div>
