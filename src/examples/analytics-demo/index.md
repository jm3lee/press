## Analytics demo walkthrough

The React playground under `app/analytics` renders a fully instrumented landing
page that streams engagement events into the ingestion API. Use this example to
understand how the provider, AutoTrack helper, and live console fit together.

### Hero and primary calls to action

The hero section is tagged with `data-track-id="hero"` and two CTA buttons.
Clicks invoke `recordInteraction('hero-cta', { variant })` so the ingestion API
captures both the target and the chosen button variant.

### Scrollable feature sections

Three feature sections map to `features`, `case-studies`, and `pricing`
identifiers. Each section declares `data-track-label` plus a JSON-encoded
`data-track-meta` payload that highlights the section ID. As you scroll, the
provider emits `view` and `view-end` pairs for every section.

### Customer story cards

A grid of story cards sits beneath the feature narrative. AutoTrack registers
nested trackers such as `data-track-id="story-northstar"`, so pressing the
"Open report" button fires an interaction event scoped to that specific story.

### Dynamic section toggle

The sidebar exposes a "Add dynamic section" toggle. When activated it reveals a
`dynamic-insight` panel that enters the DOM after the initial render. AutoTrack
notices the new node, attaches tracking metadata, and emits another set of view
events once the section reaches the viewport.

### Manual controls and event console

Sidebar controls trigger additional interactions like `pricing-contact` and a
custom heartbeat named `manual-event`. The bottom of the page renders
`<EventConsole>` which polls `/events/recent` every few seconds to display raw
payloads. Watching the console while using the controls confirms the end-to-end
flow.
