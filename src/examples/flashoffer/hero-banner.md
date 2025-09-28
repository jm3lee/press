## Hero banner

Combine the hero banner with the CTA helpers when you need a landing intro
section that links to supporting content. Reuse the same keyword arguments
described in the [Primary CTA](../#primary-cta) and [Outline CTA](../#outline-cta)
sections to set analytics attributes or alter the button order. Linking the
first outline CTA to `#preview-card` keeps the hero aligned with the
[Preview card](../#preview-card) gallery, while the second outline CTA can
mirror compliance language documented in the [Footer](../#footer).

Add a focal image to the hero by supplying `hero_image_url`. Pass
`hero_image_alt` to meet accessibility requirements and reuse
`hero_image_kwargs` for additional HTML attributes such as data tracking IDs or
`loading="eager"`.

```jinja
{% raw %}
{% set primary_kwargs = {
    "extra_classes": "shadow-lg",
    "data_tracking_id": "hero-primary",
} %}
{% set first_outline_kwargs = {
    "extra_classes": "order-3 order-sm-2",
    "data_tracking_id": "hero-preview",
} %}
{% set second_outline_kwargs = {
    "extra_classes": "order-2 order-sm-3",
    "data_tracking_id": "hero-compliance",
} %}
{{ pie.flashoffer.hero_banner(
    eyebrow="Limited-run bundles",
    title="Stone Canvas: Medusa release",
    description="Pair live session studies with downloadable references tuned "
    "for the Stone Canvas Medusa campaign.",
    primary_cta_text="Start your free trial",
    primary_cta_href="/signup",
    primary_cta_kwargs=primary_kwargs,
    first_outline_text="See preview gallery",
    first_outline_href="#preview-card",
    first_outline_kwargs=first_outline_kwargs,
    second_outline_text="Read studio policies",
    second_outline_href="/policies",
    second_outline_kwargs=second_outline_kwargs,
    hero_image_url="https://cdn.example.com/hero-visual.jpg",
    hero_image_alt="Stone Canvas hero artwork",
    hero_image_kwargs={"data_tracking_id": "hero-visual"},
) }}
{% endraw %}
```

renders as:

{% set primary_kwargs = {
    "extra_classes": "shadow-lg",
    "data_tracking_id": "hero-primary",
} %}
{% set first_outline_kwargs = {
    "extra_classes": "order-3 order-sm-2",
    "data_tracking_id": "hero-preview",
} %}
{% set second_outline_kwargs = {
    "extra_classes": "order-2 order-sm-3",
    "data_tracking_id": "hero-compliance",
} %}
{{ pie.flashoffer.hero_banner(
    eyebrow="Limited-run bundles",
    title="Stone Canvas: Medusa release",
    description="Pair live session studies with downloadable references tuned "
    "for the Stone Canvas Medusa campaign.",
    primary_cta_text="Start your free trial",
    primary_cta_href="/signup",
    primary_cta_kwargs=primary_kwargs,
    first_outline_text="See preview gallery",
    first_outline_href="#preview-card",
    first_outline_kwargs=first_outline_kwargs,
    second_outline_text="Read studio policies",
    second_outline_href="/policies",
    second_outline_kwargs=second_outline_kwargs,
    hero_image_url="https://cdn.example.com/hero-visual.jpg",
    hero_image_alt="Stone Canvas hero artwork",
    hero_image_kwargs={"data_tracking_id": "hero-visual"},
) }}

The helper applies a gradient background that matches the Press theme. Define a
`--flashoffer-hero-background` custom property in your stylesheet to supply a
different background when needed. Additional Flashoffer variables such as
`--flashoffer-hero-padding-block`, `--flashoffer-hero-visual-radius`, and
`--flashoffer-preview-overlay-background` let you adjust layout spacing,
shadows, and overlay treatments without writing new selectors.
