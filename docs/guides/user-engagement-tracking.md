# User Engagement Tracking

This guide documents practical options for measuring user engagement on
Press-generated sites that run inside a DigitalOcean App Platform private
network. The recommendations balance reliable data collection with the
constraints of private networking, controlled data flows, and minimal client
side overhead.

## Architecture overview

A typical deployment contains three cooperating services inside the App
Platform private network:

1. **Press site** – Serves the static HTML and embeds lightweight tracking
   scripts. The site has outbound access to other private services but is not
   publicly reachable over the private network.
2. **Ingestion API** – A small service (for example, FastAPI, Express, or
   Go) that receives engagement events via HTTPS from the site. It exposes an
   internal URL such as `https://engagement.internal.ondigitalocean.app`.
3. **Database** – A managed PostgreSQL, Timescale, or ClickHouse cluster with
   a private endpoint. The ingestion service connects using DigitalOcean's VPC
   networking so that no traffic leaves the private network.

When you need to move aggregates or dashboards outside the private network,
expose them through a separate reporting API or scheduled export job instead of
letting the tracking service talk directly to the public Internet.

## Data model and storage

Design the event format up front so that downstream analytics remain easy to
query. A lightweight schema works well:

```json
{
  "site": "press-docs",
  "session_id": "f0b46a0f-2c5c-4d9a-8d89-2f94ea10c018",
  "event": "view",
  "target": "hero",
  "meta": {
    "viewport": {
      "width": 1280,
      "height": 720
    },
    "scroll": 0.38,
    "duration_ms": 5200
  },
  "at": "2024-05-17T18:43:22.318Z"
}
```

Store raw events in an append-only table and create materialized views for
summary questions such as "How often do visitors reach the pricing table?"
DigitalOcean's managed PostgreSQL and Timescale handle this pattern well.

## Tracking techniques

Combine multiple complementary signals to understand how visitors interact with
the page.

### 1. Viewability observers

Use the `IntersectionObserver` API to detect when elements enter the viewport.
Attach a tracker to repeated sections such as feature callouts, pricing cards,
or testimonials. Observers give precise "first seen" timestamps and can emit
"visible for N milliseconds" metrics by recording entry and exit times.

### 2. Scroll depth sampling

Record cumulative scroll depth to understand whether readers reach the bottom
of long articles. Sample the scroll position at debounced intervals and emit a
`scroll-depth` event whenever a new threshold (for example, 25, 50, 75, 100%)
gets crossed. This complements viewability data for content without explicit
trackers.

### 3. Interaction beacons

Capture meaningful interactions such as CTA clicks, video play/pause, or tab
switches. For accessibility, prefer delegated listeners on semantic elements
(`button`, `a`, `details`). Pair each event with the current scroll depth and
the IDs of viewability trackers that are active when the interaction occurs.

### 4. Idle and dwell timers

Idle detection (via `requestIdleCallback` or a small heartbeat timer) helps you
measure true reading time. Emit a `dwell` event every N seconds while the page
has focus and the user is not idle. This highlights sections that draw attention
versus those that are skimmed quickly.

## Frontend implementation

### Data attributes for static content

Press templates can expose instrumentation points with semantic attributes:

```html
<section id="features" data-track-id="features" data-track-label="Feature Grid">
  ...
</section>
```

The React components below automatically subscribe to every element that carries
`data-track-id`. Authors can place as many trackers as they want throughout the
page without writing additional JavaScript.

### React instrumentation components

Press now ships an implementation under `app/analytics` that exports a provider
plus helper components. The snippet below focuses on the core logic; it works
with plain React 18 and does not require external analytics SDKs.

```jsx
import React, { createContext, useCallback, useEffect, useRef, useState } from "react";

const EngagementContext = createContext({
  register: () => () => {},
  recordInteraction: () => {},
});

export function EngagementProvider({ endpoint, site, children }) {
  const queueRef = useRef([]);
  const [sessionId] = useState(() => crypto.randomUUID());

  const flush = useCallback(async () => {
    if (!queueRef.current.length) return;
    const payload = queueRef.current.splice(0, queueRef.current.length);
    await fetch(endpoint, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ site, session_id: sessionId, events: payload }),
    });
  }, [endpoint, sessionId]);

  useEffect(() => {
    const id = setInterval(flush, 5000);
    return () => clearInterval(id);
  }, [flush]);

  const register = useCallback((id, meta = {}) => {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          queueRef.current.push({
            type: "view",
            target: id,
            meta: { ratio: entry.intersectionRatio, ...meta },
            at: new Date().toISOString(),
          });
        }
      }
    }, { threshold: [0.25, 0.5, 0.75, 1] });

    return element => {
      if (element) observer.observe(element);
      return () => observer.disconnect();
    };
  }, []);

  const recordInteraction = useCallback((target, data = {}) => {
    queueRef.current.push({
      type: "interaction",
      target,
      meta: data,
      at: new Date().toISOString(),
    });
  }, []);

  return (
    <EngagementContext.Provider value={{ register, recordInteraction }}>
      {children}
    </EngagementContext.Provider>
  );
}

export function ViewTracker({ trackId, children, meta }) {
  const ref = useRef(null);
  const { register } = React.useContext(EngagementContext);

  useEffect(() => register(trackId, meta)(ref.current), [register, trackId, meta]);
  return <div ref={ref} data-track-id={trackId}>{children}</div>;
}

export function useRecordInteraction() {
  const { recordInteraction } = React.useContext(EngagementContext);
  return recordInteraction;
}
```

Mount the provider once per page, ideally in a hydration script that Press
includes at the bottom of `template.html.jinja`:

```jsx
import { createRoot } from "react-dom/client";
import { EngagementProvider } from "./EngagementProvider";

const root = document.getElementById("engagement-root");
if (root) {
  createRoot(root).render(
    <EngagementProvider
      endpoint="https://engagement.internal.ondigitalocean.app/events"
      site="press-docs"
    >
      {root.dataset.hydrate === "page" && <PageInstrumentation />}
    </EngagementProvider>
  );
}
```

`PageInstrumentation` can locate all `data-track-id` elements and wrap them in
`ViewTracker` components, or you can rely on the bundled `AutoTrack` helper that
ships alongside the provider. Multiple trackers on a single page are welcome—the
provider deduplicates concurrent events by merging them in the queue before
flushing. See the [analytics engagement demo](./analytics-demo.md) for a
full-page walkthrough that pulls in the compiled script.

### Scroll and idle observers

Extend the provider with a debounced `scroll` listener:

```js
const thresholds = [0.25, 0.5, 0.75, 1];
let maxDepth = 0;
window.addEventListener("scroll", debounce(() => {
  const depth = (window.scrollY + window.innerHeight) / document.body.scrollHeight;
  const crossed = thresholds.find(t => depth >= t && maxDepth < t);
  if (crossed) {
    maxDepth = crossed;
    queueRef.current.push({
      type: "scroll-depth",
      target: "page",
      meta: { depth: crossed },
      at: new Date().toISOString(),
    });
  }
}, 250));
```

For dwell time, schedule a heartbeat that fires while the tab remains visible:

```js
let idle = false;
let lastActive = Date.now();

["mousemove", "keydown", "scroll", "focus"].forEach(event => {
  window.addEventListener(event, () => {
    idle = false;
    lastActive = Date.now();
  });
});

setInterval(() => {
  if (document.visibilityState !== "visible") return;
  if (Date.now() - lastActive > 30000) {
    idle = true;
    return;
  }
  queueRef.current.push({
    type: "dwell",
    target: "page",
    meta: { interval_ms: 15000 },
    at: new Date().toISOString(),
  });
}, 15000);
```

## Backend ingestion service

Expose a narrow, authenticated endpoint to receive batches. For example, a
FastAPI service might offer `/events` that validates the payload, appends the
records to PostgreSQL, and responds with `204 No Content`. Protect the route
with short-lived HMAC signatures or DigitalOcean's App Platform "service to
service" authentication to block arbitrary traffic from the public Internet.

Store events in a wide table:

```sql
CREATE TABLE engagement_event (
  id BIGSERIAL PRIMARY KEY,
  site TEXT NOT NULL,
  session_id UUID NOT NULL,
  event TEXT NOT NULL,
  target TEXT NOT NULL,
  meta JSONB NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Add indexes on `(site, occurred_at)` and `(event, target)` so that analytics
queries remain fast.

## Operations tips

- **Sampling:** If traffic spikes, sample less critical events (for example,
  dwell heartbeats) client-side before sending them to the API.
- **Privacy:** Avoid storing personally identifiable information. Use opaque
  session IDs and limit metadata to behavioral context.
- **Replays:** Keep the ingestion API idempotent by accepting client-generated
  event IDs. Deduplicate when necessary to guard against retry storms.
- **Dashboards:** Run read replicas or materialized views on DigitalOcean to
  expose metrics without impacting ingestion throughput.

With these pieces in place you can confidently monitor which sections visitors
reach, how long they stay, and where they interact—all while keeping the entire
pipeline inside the private network perimeter.
