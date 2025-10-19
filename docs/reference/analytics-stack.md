# Analytics stack

## Overview
Press instruments engagement analytics with a trio of services that run under
Docker Compose. React components in `app/flashoffer/flashoffer-react` emit
batched events when embedded in marketing experiences,
`analytics-backend` authenticates and validates the payload, and
`analytics-timescaledb` stores the resulting hypertable data set. The stack
provides a reproducible environment for demos and supports production-like
pipelines. Two JavaScript helpers, `EngagementProvider` and `AutoTrack`, sit at
the edge of the system and funnel page activity into the ingestion API.

## Instrumentation components
`EngagementProvider` and `AutoTrack` work together to translate front-end
activity into structured events. The provider coordinates batching, throttling,
and API calls, while AutoTrack inspects the DOM for new tracking metadata and
subscribes to visibility changes.

### Feature comparison
| Capability | EngagementProvider | AutoTrack |
| --- | --- | --- |
| Event coverage | Tracks view, view-end, interaction, dwell, and custom events | Emits view and view-end events for tracked nodes |
| Initialization | Wraps the React tree and exposes hooks such as `useEngagement` | Render `<AutoTrack selector>` inside the provider to enable observers |
| Dynamic DOM support | Handles manual calls like `recordInteraction` and `recordHeartbeat` | Watches DOM mutations and registers trackers automatically |
| Metadata handling | Accepts metadata supplied through helper calls | Parses `data-track-*` attributes and forwards the merged payload |
| Best suited for | Coordinating batching, retries, and custom analytics logic | Declarative tracking for marketing and CMS-driven content |

### Use cases
- **EngagementProvider**
  - Bootstrapping a site-wide analytics context.
  - Streaming synthetic events such as heartbeats from timers or background
    jobs.
  - Instrumenting complex UI flows that require imperative `recordInteraction`
    calls with additional metadata.
- **AutoTrack**
  - Decorating marketing content or CMS slices with tracking attributes.
  - Monitoring dynamically inserted components (for example, feature toggles or
    personalization slots) without re-mounting the provider.
  - Capturing scroll depth and section visibility with minimal React code.

### Example instrumentation
```tsx
import {
  EngagementProvider,
  AutoTrack,
  useRecordInteraction,
} from "flashoffer-react";

export function App() {
  return (
    <EngagementProvider
      endpoint="/events"
      site="marketing"
      flushInterval={2500}
      heartbeatInterval={10000}
      idleTimeout={60000}
      scrollThresholds={[0.25, 0.5, 0.75, 1]}
      viewThresholds={[0.25, 0.5, 0.75, 1]}
      maxBatch={50}
    >
      <LandingPage />
      <AutoTrack selector="[data-track-id]" />
    </EngagementProvider>
  );
}

function LandingPage() {
  const recordInteraction = useRecordInteraction();
  return (
    <section data-track-id="hero" data-track-label="Hero">
      <button
        onClick={() => recordInteraction("hero-cta", { variant: "primary" })}
      >
        Book a demo
      </button>
    </section>
  );
}
```

`EngagementProvider` handles batching and submission, while AutoTrack discovers
elements annotated with `data-track-*` attributes and emits view events as they
enter and leave the viewport. Tuning `heartbeatInterval`, `idleTimeout`,
`scrollThresholds`, `viewThresholds`, or `maxBatch` adjusts how aggressively
the provider samples and flushes data. Manual interactions call directly into
the provider with `useRecordInteraction` to supply richer metadata.

## Demo walkthrough
Embedding the helpers from `app/flashoffer/flashoffer-react` inside a marketing
page streams engagement events into the ingestion API. Use the following
walkthrough to see how the provider, AutoTrack helper, and live console fit
together.

- **Hero and primary calls to action** – The hero section is tagged with
  `data-track-id="hero"` and two CTA buttons. Clicks invoke
  `recordInteraction('hero-cta', { variant })` so the ingestion API captures
  both the target and the chosen button variant.
- **Scrollable feature sections** – Three feature sections map to `features`,
  `case-studies`, and `pricing` identifiers. Each section declares
  `data-track-label` plus a JSON-encoded `data-track-meta` payload. As you
  scroll, the provider emits `view` and `view-end` pairs for every section.
- **Customer story cards** – A grid of story cards sits beneath the feature
  narrative. AutoTrack registers nested trackers such as
  `data-track-id="story-northstar"`, so pressing the "Open report" button fires
  an interaction event scoped to that specific story.
- **Dynamic section toggle** – The sidebar exposes an "Add dynamic section"
  toggle. When activated it reveals a `dynamic-insight` panel that enters the
  DOM after the initial render. AutoTrack notices the new node, attaches
  tracking metadata, and emits another set of view events once the section
  reaches the viewport.
- **Manual controls and event console** – Sidebar controls trigger interactions
  like `pricing-contact` and a custom heartbeat named `manual-event`. The page
  renders `<EventConsole>`, which polls `/events/recent` to display raw payloads
  and confirm the end-to-end flow.

## Architecture
The analytics flow contains three stages:

1. **Client instrumentation** – `EngagementProvider` aggregates samples into
   batches and posts them to the ingestion API over HTTPS. AutoTrack observes
   the DOM and forwards structured view events to the provider.
2. **Ingestion API** – The Flask application in
   `app/flashoffer/analytics-backend` accepts the JSON payload, applies schema
   validation, and inserts rows into the hypertable with TimescaleDB-compatible
   SQL.
3. **Persistence** – TimescaleDB stores the append-only `engagement_events`
   hypertable. Native compression and retention policies can be enabled to
   manage storage costs.

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
- **Build context** – `app/flashoffer/analytics-backend` contains the Flask
  service, Alembic migrations, and pytest suite. Compose mounts the directory
  for live reloads during development.
- **Database configuration variables** – Review the summary below for the
  environment variables that control TimescaleDB connectivity.
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
  The dev image installs `requirements-dev.txt` on top of the runtime
  dependencies, so pytest is ready to go. The suite boots TimescaleDB, applies
  migrations, submits sample payloads, and truncates the hypertable when the
  run completes.

#### Database configuration summary
- `DATABASE_URL` – Full PostgreSQL connection string that may include
  credentials, port, and SSL query parameters.
- `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, and
  `DATABASE_NAME` – Discrete connection settings when you are not using
  `DATABASE_URL`.
- `DATABASE_POOL_MIN` and `DATABASE_POOL_MAX` – Optional overrides for the
  psycopg connection pool size.
- `DATABASE_SSLMODE`, `DATABASE_SSLROOTCERT`, `DATABASE_SSLCERT`,
  `DATABASE_SSLKEY`, `DATABASE_SSLPASSWORD`, `DATABASE_SSLCRL`, and
  `DATABASE_TARGET_SESSION_ATTRS` – Optional SSL overrides that supplement the
  connection options parsed from `DATABASE_URL` or the discrete settings.
- `CORS_ALLOW_ORIGINS` – Comma-separated front-end origins allowed to issue
  cross-origin requests.

#### `DATABASE_URL`
Use `DATABASE_URL` when the hosting provider gives you a ready-made connection
string. Include any SSL requirements as query parameters, such as:

```
postgresql://user:pass@host:25060/defaultdb?sslmode=require
```

When `DATABASE_URL` is set, the backend ignores the discrete host, port, user,
password, and database variables.

#### `DATABASE_HOST`
`DATABASE_HOST` selects the TimescaleDB host when `DATABASE_URL` is not set.
Combine it with `DATABASE_USER`, `DATABASE_PASSWORD`, and `DATABASE_NAME` to
describe the target instance.

#### `DATABASE_PORT`
`DATABASE_PORT` specifies the TCP port for TimescaleDB. It defaults to `5432`
when omitted.

#### `DATABASE_USER`
`DATABASE_USER` is the TimescaleDB role used for both migrations and runtime
queries. Pair it with `DATABASE_PASSWORD` for password authentication.

#### `DATABASE_PASSWORD`
`DATABASE_PASSWORD` holds the TimescaleDB password associated with
`DATABASE_USER`.

#### `DATABASE_NAME`
`DATABASE_NAME` is the database within the TimescaleDB cluster that stores the
engagement event schema.

#### Connection pool sizing
`DATABASE_POOL_MIN` and `DATABASE_POOL_MAX` tune the psycopg connection pool.
They default to `1` and `10`. Increase the values when the deployment needs more
concurrent ingestion throughput.

#### SSL overrides
When `DATABASE_URL` does not include every SSL parameter, or when you are using
discrete connection settings, supply the remaining options through the
`DATABASE_SSL*` environment variables listed above. Each value is passed
directly to psycopg's connection factory.

#### `CORS_ALLOW_ORIGINS`
`CORS_ALLOW_ORIGINS` enumerates front-end origins allowed to call the backend.
For local development it defaults to `http://localhost:5173`.

### flashoffer-react
- **Purpose** – `app/flashoffer/flashoffer-react` packages the React
  instrumentation helpers (`EngagementProvider`, `AutoTrack`, and
  `EventConsole`) for consumption in marketing front-ends.
- **Tooling** – Install dependencies and run the build to generate distributable
  assets:
  ```bash
  cd app/flashoffer/flashoffer-react
  npm install
  npm run build
  ```
  The Vite build emits ESM and CommonJS bundles so applications can import the
  helpers directly or publish a compiled asset for static sites.

### flashoffer / flashoffer-dev
- **Purpose** – Serve the Flashoffer marketing demo either as a static preview
  (`flashoffer`) or via the Vite dev server (`flashoffer-dev`).
- **Analytics wiring** – Compose exports
  `VITE_FLASHOFFER_ANALYTICS_ENDPOINT` and
  `VITE_FLASHOFFER_ANALYTICS_RECENT_URL` so the demo posts batched events to
  `analytics-backend` at `http://localhost:8001` by default.
- **Overrides** – Set `FLASHOFFER_ANALYTICS_ENDPOINT` or
  `FLASHOFFER_ANALYTICS_RECENT_URL` in your environment to target alternate
  ingestion hosts without editing Compose files.

## Local workflow
1. Start the database and ingestion API:
   ```bash
   docker compose up analytics-timescaledb analytics-backend
   ```
   Wait until the Flask logs show `Running on http://0.0.0.0:8000/`. Port `8001`
   on the host forwards to the container's `8000`.
2. Import the React helpers into your marketing site or demo application and run
   it alongside the backend. The console lists captured events in real time.
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
