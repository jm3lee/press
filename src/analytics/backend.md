## Analytics backend service

The analytics backend pairs a lightweight Flask ingestion API with a managed
TimescaleDB instance. It accepts the batched engagement payload emitted by
`EngagementProvider.jsx`, persists events as an append-only hypertable, and
exposes health, discovery, and recent-event endpoints for monitoring.

### Containers

Two new services are defined in `docker-compose.yml`:

- `analytics-timescaledb` runs TimescaleDB 14 with a persistent Docker volume.
- `analytics-backend` builds the Flask application from `app/analytics-backend`.

Both containers start with `docker compose up analytics-timescaledb
analytics-backend`. TimescaleDB listens on port `5433` on the host, while the
Flask service is available at `http://localhost:8001`.

### Environment variables

The backend reads its configuration from the following variables:

- `DATABASE_HOST` – hostname for the TimescaleDB instance.
- `DATABASE_PORT` – port for the database (defaults to `5432`).
- `DATABASE_USER` – database role used for inserts.
- `DATABASE_PASSWORD` – credential for the configured role.
- `DATABASE_NAME` – database that contains the hypertable.
- `CORS_ALLOW_ORIGINS` – optional comma-separated list of origins allowed to
  call the API with credentials (set to `http://localhost:5173` for the demo).

Docker Compose sets these values automatically. When running the Flask app
outside Docker you must export them manually.

### HTTP endpoints

- `POST /events` ingests a batch of engagement events. Payloads should match
  the structure emitted by `EngagementProvider.jsx`.
- `GET /events/recent` returns the most recent events (defaults to the 25 most
  recent rows). Use `?limit=50` to adjust the window during demos.
- `GET /health` verifies TimescaleDB connectivity.
- `GET /config` returns the database host, port, and name.

### Local testing

Run the test suite inside the container to validate schema migrations and the
ingestion endpoint:

```bash
docker compose run --rm analytics-backend pytest
```

The fixture bootstraps TimescaleDB, performs an end-to-end ingestion request,
and truncates the hypertable after the test run.
