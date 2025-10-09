# Flashoffer

The Flashoffer workspace bundles the services and libraries that power the
Flashoffer experience. Use this guide to locate project entry points and the
shared documentation that now lives in a single location.

## Directory Overview

- `analytics-backend/` – Event ingestion APIs and supporting workers.
- `analytics-db/` – Database schema and migrations for analytics workloads.
- `backend-common/` – Shared backend utilities and domain models.
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
