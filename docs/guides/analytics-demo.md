# Analytics engagement demo

This walkthrough spins up the Flask ingestion API, the TimescaleDB instance,
and the React playground that emits engagement events. The end result is a live
page that streams view, scroll, dwell, and interaction events into
TimescaleDB while a console renders the captured payloads.

## Prerequisites

- Docker Desktop (or a compatible runtime) for the backend containers.
- Node.js 20+ and npm for the Vite development server.

## Start the backend

The `docker-compose.yml` file already wires the ingestion API and database
behind sensible defaults. Launch them in a dedicated shell:

```bash
docker compose up analytics-timescaledb analytics-backend
```

Wait until the Flask service logs `Running on http://0.0.0.0:8000/`. The compose
file enables CORS for `http://localhost:5173`, which lets the Vite dev server
post events with credentials.

## Run the React demo

Open a second terminal and install dependencies before starting Vite:

```bash
cd app/analytics
npm install
npm run dev
```

Vite exposes the playground at `http://localhost:5173`. The landing page mounts
`EngagementProvider`, renders several scrollable sections with instrumentation
attributes, and polls `/events/recent` to display captured events.

## Explore the instrumentation

1. Scroll slowly through the feature sections to trigger `view` and `view-end`
   pairs.
2. Use the hero buttons or story cards to send `interaction` events with extra
   metadata.
3. Toggle the dynamic section in the sidebar to watch AutoTrack detect elements
   added after the initial render.
4. Leave the tab focused for 15 seconds to emit `dwell` heartbeats.

Every action surfaces in the live console. You can also inspect the raw rows in
TimescaleDB:

```bash
docker compose exec analytics-timescaledb \
  psql -U analytics -d analytics \
  -c "SELECT event_type, target, occurred_at, meta FROM engagement_events ORDER BY received_at DESC LIMIT 5;"
```

Use `Ctrl+C` in each terminal to stop the demo when you are finished.
