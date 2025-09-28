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
- **Build context** – `app/analytics-backend` contains the Flask service, Alembic
  migrations, and pytest suite. Compose mounts the directory for live reloads
  during development.
- **Environment variables** – The service reads its database configuration from
  `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, and
  `DATABASE_NAME`. `CORS_ALLOW_ORIGINS` lists permitted front-end origins (the
  demo defaults to `http://localhost:5173`). Export the same values when running
  the app outside Docker.
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
  backend. Ensure CORS settings include the origin when running against a remote
  ingestion service.

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
- Run `docker compose ps` to confirm both containers are healthy and exposing the
  expected ports.
- If the demo cannot reach the API, verify that the browser origin matches
  `CORS_ALLOW_ORIGINS` and that port `8001` remains available on the host.
