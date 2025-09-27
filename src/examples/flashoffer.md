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

<div
  class="accordion mb-4"
  id="flashoffer-primary-cta-code"
>
  <div class="accordion-item">
    <h2
      class="accordion-header"
      id="flashoffer-primary-cta-code-heading"
    >
      <button
        class="accordion-button collapsed"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#flashoffer-primary-cta-code-body"
        aria-expanded="false"
        aria-controls="flashoffer-primary-cta-code-body"
      >
        View template code
      </button>
    </h2>
    <div
      id="flashoffer-primary-cta-code-body"
      class="accordion-collapse collapse"
      aria-labelledby="flashoffer-primary-cta-code-heading"
      data-bs-parent="#flashoffer-primary-cta-code"
    >
      <div class="accordion-body">
<pre><code class="language-jinja">{{ pie.flashoffer.primary_cta("Start your free trial", "/signup") }}</code></pre>
      </div>
    </div>
  </div>
</div>

renders as:

{{ pie.flashoffer.primary_cta("Start your free trial", "/signup") }}

## Outline CTA

Pair the outline helper with the primary button to offer a secondary action.

<div
  class="accordion mb-4"
  id="flashoffer-outline-cta-code"
>
  <div class="accordion-item">
    <h2
      class="accordion-header"
      id="flashoffer-outline-cta-code-heading"
    >
      <button
        class="accordion-button collapsed"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#flashoffer-outline-cta-code-body"
        aria-expanded="false"
        aria-controls="flashoffer-outline-cta-code-body"
      >
        View template code
      </button>
    </h2>
    <div
      id="flashoffer-outline-cta-code-body"
      class="accordion-collapse collapse"
      aria-labelledby="flashoffer-outline-cta-code-heading"
      data-bs-parent="#flashoffer-outline-cta-code"
    >
      <div class="accordion-body">
<pre><code class="language-jinja">{{ pie.flashoffer.outline_cta("Talk to sales", "/contact") }}</code></pre>
      </div>
    </div>
  </div>
</div>

renders as:

{{ pie.flashoffer.outline_cta("Talk to sales", "/contact") }}

## Customize attributes

You can combine helpers with additional classes and attributes to match your
layout or analytics requirements.

<div
  class="accordion mb-4"
  id="flashoffer-customize-code"
>
  <div class="accordion-item">
    <h2
      class="accordion-header"
      id="flashoffer-customize-code-heading"
    >
      <button
        class="accordion-button collapsed"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#flashoffer-customize-code-body"
        aria-expanded="false"
        aria-controls="flashoffer-customize-code-body"
      >
        View template code
      </button>
    </h2>
    <div
      id="flashoffer-customize-code-body"
      class="accordion-collapse collapse"
      aria-labelledby="flashoffer-customize-code-heading"
      data-bs-parent="#flashoffer-customize-code"
    >
      <div class="accordion-body">
<pre><code class="language-jinja">{{ pie.flashoffer.outline_cta(
    "View partner pricing",
    "https://example.com/pricing",
    extra_classes="mt-3",
    rel="noopener",
    target="_blank",
    data_tracking_id="hero-secondary",
) }}</code></pre>
      </div>
    </div>
  </div>
</div>

renders as:

{{ pie.flashoffer.outline_cta(
    "View partner pricing",
    "https://example.com/pricing",
    extra_classes="mt-3",
    rel="noopener",
    target="_blank",
    data_tracking_id="hero-secondary",
) }}

## Hero banner

Combine the hero banner with the CTA helpers when you need a landing intro
section that links to supporting content. Reuse the same keyword arguments
described in the [Primary CTA](#primary-cta) and [Outline CTA](#outline-cta)
sections to set analytics attributes or alter the button order. Linking the
first outline CTA to `#preview-card` keeps the hero aligned with the
[Preview card](#preview-card) gallery, while the second outline CTA can mirror
compliance language documented in the [Footer](#footer).

```jinja
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
) }}
```

renders as:

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
) }}

## Preview card

Combine the preview card with CTA helpers when a template needs to hide the
full image behind a tap target.

<div
  class="accordion mb-4"
  id="flashoffer-preview-card-code"
>
  <div class="accordion-item">
    <h2
      class="accordion-header"
      id="flashoffer-preview-card-code-heading"
    >
      <button
        class="accordion-button collapsed"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#flashoffer-preview-card-code-body"
        aria-expanded="false"
        aria-controls="flashoffer-preview-card-code-body"
      >
        View template code
      </button>
    </h2>
    <div
      id="flashoffer-preview-card-code-body"
      class="accordion-collapse collapse"
      aria-labelledby="flashoffer-preview-card-code-heading"
      data-bs-parent="#flashoffer-preview-card-code"
    >
      <div class="accordion-body">
<pre><code class="language-jinja">{% set preview = {
    "image_url": "https://cdn.example.com/image.jpg",
    "alt_text": "Gallery preview",
    "link_href": "https://example.com/gallery",
    "caption": "Captured in natural light.",
} %}
{{ pie.flashoffer.preview_card(preview) }}
```

Pass `overlay_text` or `overlay_button_text` to tailor the message revealed on
hover or tap. Both parameters escape plain strings while preserving
`markupsafe.Markup` instances, so you can safely inject trusted HTML when
needed.

```jinja
{{ pie.flashoffer.preview_card(
    preview,
    overlay_text="Tap to reveal the <em>full pose</em>",
    overlay_button_text="Open reference",
) }}
```

{% set preview = {
    "image_url": "https://seattlefigurestudio.sfo3.cdn.digitaloceanspaces.com/landing/favicon-48x48.png",
    "alt_text": "Seattle Figure Studio Favicon",
    "link_href": "https://seattlefigurestudio.com",
    "caption": "a cool place",
} %}
{{ pie.flashoffer.preview_card(preview) }}

## Preview grid

Use the preview grid when a landing page needs to showcase more than one
study bundle without immediately exposing the underlying figure photography.
The layout keeps the cards aligned across breakpoints while the helper ensures
each card carries consistent Flashoffer styling.

The overlay button created by `pie.flashoffer.preview_card` is wired up by the
base template's JavaScript in `src/templates/template.html.jinja`, so visitors
must click the configured overlay button before any NSFW content is revealed.
No additional script is required inside your page.

The reusable partial at
`src/templates/examples/flashoffer-card-grid.html.jinja` iterates through
`card_list` and calls the helper for every entry. This keeps the markup
centralised and makes it easy to swap in new cards or update the button text
in one place.

<div
  class="accordion mb-4"
  id="flashoffer-preview-grid-code"
>
  <div class="accordion-item">
    <h2
      class="accordion-header"
      id="flashoffer-preview-grid-code-heading"
    >
      <button
        class="accordion-button collapsed"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#flashoffer-preview-grid-code-body"
        aria-expanded="false"
        aria-controls="flashoffer-preview-grid-code-body"
      >
        View template code
      </button>
    </h2>
    <div
      id="flashoffer-preview-grid-code-body"
      class="accordion-collapse collapse"
      aria-labelledby="flashoffer-preview-grid-code-heading"
      data-bs-parent="#flashoffer-preview-grid-code"
    >
      <div class="accordion-body">
<pre><code class="language-jinja">&lt;div
  class=&quot;alert alert-warning d-flex align-items-center gap-2&quot;
  role=&quot;alert&quot;
&gt;
  &lt;span class=&quot;fw-semibold text-uppercase small&quot;&gt;Heads up&lt;/span&gt;
  &lt;span&gt;Preview links should comply with your terms of service.&lt;/span&gt;
&lt;/div&gt;

{% set card_list = [
    {
        &quot;image_url&quot;: &quot;https://picsum.photos/seed/flashoffer-1/640/480&quot;,
        &quot;alt_text&quot;: &quot;Dynamic seated pose&quot;,
        &quot;link_href&quot;: &quot;https://example.com/bundles/dynamic&quot;,
        &quot;caption&quot;: &quot;45-minute seated gestures with charcoal studies.&quot;,
    },
    {
        &quot;image_url&quot;: &quot;https://picsum.photos/seed/flashoffer-2/640/480&quot;,
        &quot;alt_text&quot;: &quot;Contrapposto profile pose&quot;,
        &quot;link_href&quot;: &quot;https://example.com/bundles/profile&quot;,
        &quot;caption&quot;: &quot;Standing contrapposto sequence captured at 5 angles.&quot;,
    },
    {
        &quot;image_url&quot;: &quot;https://picsum.photos/seed/flashoffer-3/640/480&quot;,
        &quot;alt_text&quot;: &quot;Foreshortened reclining pose&quot;,
        &quot;link_href&quot;: &quot;https://example.com/bundles/reclining&quot;,
        &quot;caption&quot;: &quot;Foreshortened reclining study with lighting notes.&quot;,
    },
] %}

{% include &quot;examples/flashoffer-card-grid.html.jinja&quot; %}

&lt;div class=&quot;mt-4 d-grid gap-3 d-sm-flex justify-content-center&quot;&gt;
  {{ pie.flashoffer.primary_cta(
      &quot;Download the full bundle&quot;,
      &quot;https://example.com/bundles/download&quot;
  ) }}
  {{ pie.flashoffer.outline_cta(
      &quot;See studio policies&quot;,
      &quot;https://example.com/policies&quot;
  ) }}
&lt;/div&gt;</code></pre>
      </div>
    </div>
  </div>
</div>

renders as:

<div
  class="alert alert-warning d-flex align-items-center gap-2"
  role="alert"
>
  <span class="fw-semibold text-uppercase small">Heads up</span>
  <span>Preview links should comply with your terms of service.</span>
</div>

{% set card_list = [
    {
        "image_url": "https://picsum.photos/seed/flashoffer-1/640/480",
        "alt_text": "Dynamic seated pose",
        "link_href": "https://example.com/bundles/dynamic",
        "caption": "45-minute seated gestures with charcoal studies.",
    },
    {
        "image_url": "https://picsum.photos/seed/flashoffer-2/640/480",
        "alt_text": "Contrapposto profile pose",
        "link_href": "https://example.com/bundles/profile",
        "caption": "Standing contrapposto sequence captured at 5 angles.",
    },
    {
        "image_url": "https://picsum.photos/seed/flashoffer-3/640/480",
        "alt_text": "Foreshortened reclining pose",
        "link_href": "https://example.com/bundles/reclining",
        "caption": "Foreshortened reclining study with lighting notes.",
    },
] %}
{% include "examples/flashoffer-card-grid.html.jinja" %}

<div class="mt-4 d-grid gap-3 d-sm-flex justify-content-center">
  {{ pie.flashoffer.primary_cta(
      "Download the full bundle",
      "https://example.com/bundles/download"
  ) }}
  {{ pie.flashoffer.outline_cta(
      "See studio policies",
      "https://example.com/policies"
  ) }}
</div>

## Footer

Use the footer helper to render the contact information block.

<div
  class="accordion mb-4"
  id="flashoffer-footer-code"
>
  <div class="accordion-item">
    <h2
      class="accordion-header"
      id="flashoffer-footer-code-heading"
    >
      <button
        class="accordion-button collapsed"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#flashoffer-footer-code-body"
        aria-expanded="false"
        aria-controls="flashoffer-footer-code-body"
      >
        View template code
      </button>
    </h2>
    <div
      id="flashoffer-footer-code-body"
      class="accordion-collapse collapse"
      aria-labelledby="flashoffer-footer-code-heading"
      data-bs-parent="#flashoffer-footer-code"
    >
      <div class="accordion-body">
<pre><code class="language-jinja">{{ pie.flashoffer.footer(
    left_prefix=&quot;©&amp;nbsp;&quot;,
    site_name=&quot;Seattle Figure Studio&quot;,
    site_href=&quot;https://seattlefigurestudio.com&quot;,
    rights_statement=&quot;All rights reserved.&quot;,
    email_label=&quot;brian@seattlefigurestudio.com&quot;,
) }}</code></pre>
      </div>
    </div>
  </div>
</div>

renders as:

{{ pie.flashoffer.footer() }}
