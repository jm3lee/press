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
    eyebrow="CAMPAIGN TOOLKIT",
    title="Launch coordinated offers in minutes.",
    description="Flashoffer ships reusable hero, CTA, and preview components "
    "so teams can publish landing experiments without bespoke design cycles.",
    primary_cta_text="Explore Flashoffer components",
    primary_cta_href="https://example.com/flashoffer",
    primary_cta_kwargs=primary_kwargs,
    first_outline_text="Contact support",
    first_outline_href="mailto:support@example.com",
    first_outline_kwargs=first_outline_kwargs,
    second_outline_text="View documentation",
    second_outline_href="https://example.com/docs",
    second_outline_kwargs=second_outline_kwargs,
    hero_image_url="https://picsum.photos/seed/flashoffer-hero/720/480",
    hero_image_alt="Mock dashboard showcasing offer performance",
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
    eyebrow="CAMPAIGN TOOLKIT",
    title="Launch coordinated offers in minutes.",
    description="Flashoffer ships reusable hero, CTA, and preview components "
    "so teams can publish landing experiments without bespoke design cycles.",
    primary_cta_text="Explore Flashoffer components",
    primary_cta_href="https://example.com/flashoffer",
    primary_cta_kwargs=primary_kwargs,
    first_outline_text="Contact support",
    first_outline_href="mailto:support@example.com",
    first_outline_kwargs=first_outline_kwargs,
    second_outline_text="View documentation",
    second_outline_href="https://example.com/docs",
    second_outline_kwargs=second_outline_kwargs,
    hero_image_url="https://picsum.photos/seed/flashoffer-hero/720/480",
    hero_image_alt="Mock dashboard showcasing offer performance",
    hero_image_kwargs={"data_tracking_id": "hero-visual"},
) }}

The helper applies a gradient background that matches the Press theme. Define a
`--flashoffer-hero-background` custom property in your stylesheet to supply a
different background when needed. Additional Flashoffer variables such as
`--flashoffer-hero-padding-block`, `--flashoffer-hero-visual-radius`, and
`--flashoffer-preview-overlay-background` let you adjust layout spacing,
shadows, and overlay treatments without writing new selectors.
