# Analytics stack

## Overview
Press instruments engagement analytics with a trio of services that run under
Docker Compose. The React playground in `app/analytics` emits batched events,
`analytics-backend` authenticates and validates the payload, and
`analytics-timescaledb` stores the resulting hypertable data set. The stack
provides a reproducible environment for demos and supports production-like
pipelines.

## Architecture
The analytics flow contains three stages:

1. **Client instrumentation** – `EngagementProvider` in `app/analytics` tracks
   views, interactions, and dwell events. It aggregates samples into batches
   and posts them to the ingestion API over HTTPS.
2. **Ingestion API** – The Flask application in `app/analytics-backend` accepts
   the JSON payload, applies schema validation, and inserts rows into the
   hypertable with TimescaleDB-compatible SQL.
3. **Persistence** – TimescaleDB stores the append-only
   `engagement_events` hypertable. Native compression and retention policies can
   be enabled to manage storage costs.

All containers share the default Docker network created by Compose. The backend
discovers the database via the `analytics-timescaledb` hostname, while the demo
application reaches the API through the host-mapped port.

## Services

### analytics-timescaledb
- **Image** – `timescale/timescaledb:latest-pg14` with PostgreSQL 14 and
  TimescaleDB extensions.
- **Port mapping** – `5433` on the host forwards to `5432` in the container so
  you can run a local PostgreSQL instance side-by-side.
- **Persistent volume** – `analytics_timescale_data` stores cluster state,
  allowing upgrades or container restarts without losing demo data.
- **Bootstrap credentials** – Compose sets `analytics` as the user, password,
  and database. Override the variables when connecting to production-grade
  infrastructure.
- **psql access** – Inspect recent events directly from the host:
  ```bash
  docker compose exec analytics-timescaledb \
    psql -U analytics -d analytics \
    -c "SELECT event_type, target, occurred_at, meta FROM engagement_events \
        ORDER BY received_at DESC LIMIT 5;"
  ```

### analytics-backend
- **Build context** – `app/analytics-backend` contains the Flask service,
  Alembic migrations, and pytest suite. Compose mounts the directory for live
  reloads during development.
- **Environment variables** – The service reads its database configuration from
  `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, and
  `DATABASE_NAME`. `CORS_ALLOW_ORIGINS` lists permitted front-end origins (the
  demo defaults to `http://localhost:5173`). Export the same values when
  running the app outside Docker.
- **HTTP interface** –
  - `POST /events` ingests a batch of engagement events emitted by the
    playground.
  - `GET /events/recent` streams the latest rows for the on-page console.
  - `GET /health` verifies database connectivity.
  - `GET /config` exposes the resolved database host, port, and name.
- **Testing** – Run end-to-end ingestion tests inside the container:
  ```bash
  docker compose run --rm analytics-backend pytest
  ```
  The suite boots TimescaleDB, applies migrations, submits sample payloads, and
  truncates the hypertable when the run completes.

### analytics
- **Purpose** – Hosts the Vite playground in `app/analytics` that demonstrates
  the instrumentation bundle.
- **Tooling** – Install dependencies and start the dev server in a separate
  terminal:
  ```bash
  cd app/analytics
  npm install
  npm run dev
  ```
  Vite binds to `http://localhost:5173` by default and proxies API calls to the
  backend. Ensure CORS settings include the origin when running against a
  remote ingestion service.

## Instrumentation guide

### EngagementProvider
`EngagementProvider` wraps the React application and exposes context helpers
for manual event recording. Key capabilities include:

- **Session orchestration** – Generates a stable session identifier, batches
  events, and retries failed submissions with exponential backoff.
- **Event catalog** – Supports `view`, `view-end`, `interaction`, and
  `heartbeat` events with strongly typed payloads.
- **Custom events** – `recordEvent` enables domain-specific payloads while
  preserving the envelope required by the ingestion API.
- **Transport controls** – Accepts `endpoint`, `flushInterval`, and
  `batchSize` props so high-traffic embeds can tune delivery.

Use `EngagementProvider` when you need deterministic control over what gets
recorded, such as feature-flag experiments or custom funnels where the
component tree is already aware of the relevant user actions.

**Use cases**

- Measuring controlled experiments or A/B tests with bespoke success metrics.
- Recording authenticated user journeys where React components already know the
  account context.
- Capturing low-volume but high-value milestones that should never be batched
  away by automated tooling.

```tsx
import { EngagementProvider, useEngagement } from "./analytics";

function PricingCta() {
  const { recordInteraction } = useEngagement();

  return (
    <button
      onClick={() => recordInteraction("pricing-contact", { surface: "hero" })}
    >
      Talk to sales
    </button>
  );
}

export function App() {
  return (
    <EngagementProvider endpoint="/events">
      <PricingCta />
    </EngagementProvider>
  );
}
```

### AutoTrack
`AutoTrack` augments the provider by scanning the DOM for
`data-track-*` attributes and registering observers. Its feature set covers:

- **Declarative wiring** – Trackers can be attached without importing React
  hooks, allowing content authors to instrument sections directly in JSX.
- **Mutation awareness** – Automatically instruments nodes that appear after
  hydration, such as lazy-loaded sections or CMS-driven inserts.
- **Viewport observation** – Emits paired `view` and `view-end` events using
  `IntersectionObserver` so long scroll pages remain accurately measured.
- **Hierarchical context** – Inherits `data-track-label` and `data-track-meta`
  to produce rich event metadata without manual merges.

Reach for `AutoTrack` when you need broad coverage across marketing pages, want
to minimize manual wiring, or must capture content that renders asynchronously.

**Use cases**

- Instrumenting CMS-driven landing pages where marketers control markup.
- Tracking interaction hotspots across long-form content without manual hooks.
- Monitoring dynamically injected widgets, testimonials, or promo banners.

```tsx
import { EngagementProvider, AutoTrack } from "./analytics";

export function LandingPage() {
  return (
    <EngagementProvider endpoint="/events">
      <AutoTrack>
        <section data-track-id="hero" data-track-label="Hero">
          <button data-track-id="hero-cta">Start free trial</button>
        </section>
      </AutoTrack>
    </EngagementProvider>
  );
}
```

### Provider versus AutoTrack

| Capability              | EngagementProvider                              | AutoTrack                               |
| ----------------------- | ------------------------------------------------ | --------------------------------------- |
| Event APIs              | Hooks: `recordInteraction`, `recordView`, etc.  | Attribute-driven                        |
| Declarative markup      | Manual by default                               | `data-track-*` attributes                |
| Auto discovery          | None                                            | Scans DOM with a mutation observer       |
| Dynamic content support | Through custom code                             | Native via observer                      |
| Best for                | Targeted funnels and bespoke metrics            | Broad coverage on marketing surfaces     |

Combine both when you want automatic coverage but still need bespoke events,
such as mixing auto-instrumented sections with explicit experiment logging.

## Demo walkthrough
The React playground under `app/analytics` renders a fully instrumented landing
page that streams engagement events into the ingestion API. Use this reference
to see how the provider, AutoTrack helper, and live console fit together.

- **Hero and primary calls to action** – The hero section is tagged with
  `data-track-id="hero"` and two CTA buttons. Clicks invoke
  `recordInteraction("hero-cta", { variant })` so the ingestion API captures
  both the target and the chosen button variant.
- **Scrollable feature sections** – Three feature sections map to `features`,
  `case-studies`, and `pricing` identifiers. Each section declares
  `data-track-label` plus a JSON-encoded `data-track-meta` payload that
  highlights the section ID. As you scroll, the provider emits `view` and
  `view-end` pairs for every section.
- **Customer story cards** – A grid of story cards sits beneath the feature
  narrative. AutoTrack registers nested trackers such as
  `data-track-id="story-northstar"`, so pressing the "Open report" button
  fires an interaction event scoped to that specific story.
- **Dynamic section toggle** – The sidebar exposes an "Add dynamic section"
  toggle. When activated it reveals a `dynamic-insight` panel that enters the
  DOM after the initial render. AutoTrack notices the new node, attaches
  tracking metadata, and emits another set of view events once the section
  reaches the viewport.
- **Manual controls and event console** – Sidebar controls trigger additional
  interactions like `pricing-contact` and a custom heartbeat named
  `manual-event`. The bottom of the page renders `<EventConsole>` which polls
  `/events/recent` every few seconds to display raw payloads. Watching the
  console while using the controls confirms the end-to-end flow.

## Local workflow
1. Start the database and ingestion API:
   ```bash
   docker compose up analytics-timescaledb analytics-backend
   ```
   Wait until the Flask logs show `Running on http://0.0.0.0:8000/`. Port `8001`
   on the host forwards to the container's `8000`.
2. Launch the Vite demo as described above and open the site in a browser. The
   console lists captured events in real time.
3. Experiment with scroll, interaction, and dwell instrumentation. Each action
   appears immediately in the backend logs and TimescaleDB queries.
4. Stop the stack with `Ctrl+C` in each terminal. The Docker volume preserves
   TimescaleDB data for the next session.

## Production considerations
- Swap the Compose-provided credentials for managed secrets before exposing the
  API publicly. Restrict network access to trusted front-end origins.
- Enable TimescaleDB compression and retention policies to manage hypertable
  size. Run maintenance commands through the database container or a managed
  service console.
- Treat the ingestion API as write-heavy: monitor connection counts, apply rate
  limiting when embedding the instrumentation bundle in high-traffic sites, and
  forward structured logs to your observability stack.

## Troubleshooting
- Use `docker compose logs analytics-backend` to inspect ingestion errors or
  schema mismatches.
- Run `docker compose ps` to confirm both containers are healthy and exposing
  the expected ports.
- If the demo cannot reach the API, verify that the browser origin matches
  `CORS_ALLOW_ORIGINS` and that port `8001` remains available on the host.
