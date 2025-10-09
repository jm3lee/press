# Flashoffer

The Flashoffer workspace bundles the services and libraries that power the
Flashoffer experience. Use this guide to locate project entry points and the
shared documentation that now lives in a single location.

## Directory Overview

- `analytics-backend/` – Event ingestion APIs and supporting workers.
- `analytics-db/` – Database schema and migrations for analytics workloads.
- `backend-common/` – Shared backend utilities and domain models.
- `campaign-backend/` – Countdown metadata API consumed by widgets.
- `campaign_manager/` – React + FastAPI admin experience for campaign CRUD.
- `flashoffer-demo/` – Reference deployment that exercises the full stack.
- `flashoffer-react/` – Public React component library for Flashoffer embeds.
- `quiz-backend/` – Services that deliver quiz content and record responses.
- `docs/` – Consolidated workspace documentation.

## Documentation

All Flashoffer documents reside in `app/flashoffer/docs`. Organize new
references beneath that directory by product area (for example,
`docs/flashoffer-react/`). Keep existing relative links intact when moving or
adding files so TypeDoc and other generators resolve content correctly.

## Conventions

- Update this README when adding or removing major packages so the directory
  overview stays accurate.
- Keep documentation and engineering guides synchronized. When you revise a
  service or library, update the relevant files under `docs/` in the same
  change.

## Authentication

Flashoffer backend services share a bearer-token workflow managed by the
campaign manager. The admin interface mints tokens and downstream APIs validate
requests with the shared secret. Every write or read endpoint in the analytics,
quiz, and campaign services now expects an `Authorization: Bearer <token>`
header. Health checks, configuration dumps, and `OPTIONS` preflight handlers
remain unauthenticated so load balancers and browsers can probe service status.

### Configuration

Set the following environment variables (or provide the equivalents through
your secret store) for each container:

- `CAMPAIGN_MANAGER_SECRET_KEY` (required) – signing key used by the campaign
  manager and downstream services when creating or validating tokens.
- `CAMPAIGN_MANAGER_ADMIN_USERNAME` (optional, defaults to `admin`) – subject
  embedded in minted tokens.
- `CAMPAIGN_MANAGER_TOKEN_TTL_SECONDS` (optional, defaults to 28,800 seconds) –
  maximum age accepted when validating bearer tokens.

Service-specific overrides are available when deployments need separate
credentials:

- `ANALYTICS_BACKEND_SECRET_KEY`, `QUIZ_BACKEND_SECRET_KEY`, and
  `CAMPAIGN_BACKEND_SECRET_KEY` replace the shared secret for the respective
  Flask apps.
- `*_AUTH_SUBJECT` and `*_TOKEN_TTL_SECONDS` follow the same pattern for the
  token subject and expiry window.

Update Docker Compose files, Kubernetes manifests, or platform-specific
configuration to surface these values. Local development defaults are provided
in `docker-compose.yml` for convenience.
