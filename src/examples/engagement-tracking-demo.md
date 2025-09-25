
This page shows how to embed the engagement tracking bundle generated from
`app/analytics`. The script watches for elements tagged with `data-track-id`
and emits view, scroll depth, interaction, and dwell events to a private
endpoint.

## 1. Mount the provider

Add a lightweight root container to the template and load the compiled bundle.
The provider reads configuration from `data-` attributes so no extra JavaScript
is needed in the page itself.

```html
<div
  data-engagement-root
  data-endpoint="https://engagement.internal.ondigitalocean.app/events"
  data-site="press-docs"
  data-selector="[data-track-id]"
></div>
<script type="module" src="/static/js/analytics.js" defer></script>
```

## 2. Tag the sections you care about

Use semantic markup and add `data-track-id` plus an optional human readable
label. The bundle automatically registers each element with an
`IntersectionObserver` so the ingestion API receives both `view` and `view-end`
messages.

```html
<section data-track-id="hero" data-track-label="Hero">
  <h1>Hero</h1>
  <p>Scroll to explore view and interaction tracking.</p>
  <button data-track-id="hero-cta">Call to Action</button>
</section>

<section data-track-id="features" data-track-label="Feature Grid">
  <h2>Features</h2>
  <p>Each section is automatically tracked for viewability.</p>
</section>

<section data-track-id="pricing" data-track-label="Pricing">
  <h2>Pricing</h2>
  <p>Scroll depth and dwell events are queued while you read.</p>
</section>
```

## 3. Record custom interactions

For React islands, use the exported `useRecordInteraction` hook to associate
clicks or other behaviours with the active view targets and scroll position.

```jsx
import { useRecordInteraction } from '/static/js/analytics.js'

function PricingCTA() {
  const recordInteraction = useRecordInteraction('pricing-cta')
  return (
    <button
      type="button"
      onClick={() => recordInteraction('pricing-cta', { plan: 'scale' })}
    >
      Choose the Scale plan
    </button>
  )
}
```

With those snippets in place the provider batches events, flushes them to the
private ingestion API, and automatically resumes tracking when new elements are
added to the DOM.
