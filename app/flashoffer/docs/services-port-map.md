# Flashoffer Service Port Map

| Service           | Host Port | Container Port | Override               |
|-------------------|-----------|----------------|------------------------|
| analytics-backend | 8001      | 8000           | none                   |
| analytics-db      | 5433      | 5432           | none                   |
| campaign-backend  | n/a       | 8000           | n/a (internal)         |
| campaign-manager  | 5174      | 4173           | CAMPAIGN_MANAGER_PORT  |
| flashoffer        | 4173, 80  | 4173, 80       | FLASHOFFER_PORT        |
| flashoffer-dev    | 5173      | 5173           | FLASHOFFER_DEV_PORT    |
| nginx-dev         | 80        | 80             | none                   |
| quiz-backend      | 8002      | 8000           | none                   |
| quiz-manager      | 5175      | 5175           | QUIZ_MANAGER_PORT      |

This reference lists the default Docker port mappings for the Flashoffer
workspace. Use it to confirm which host ports are reserved and which
environment variables override those mappings when you run multiple services in
development.

## Web Applications

- **flashoffer-dev**
  - Purpose: Vite-powered marketing demo with hot reload.
  - Host → container: `5173 → 5173`.
  - Override: `FLASHOFFER_DEV_PORT`.
  - Compose files: `docker-compose.yml`, `app/flashoffer/docker/flashoffer.yml`.

- **flashoffer**
  - Purpose: Production-mode marketing demo.
  - Host → container: `4173 → 4173` and `80 → 80`.
  - Override: `FLASHOFFER_PORT`.
  - Compose files: `docker-compose.yml`, `app/flashoffer/docker/flashoffer.yml`.

- **quiz-manager**
  - Purpose: Standalone React UI for quiz content ingestion.
  - Host → container: `5175 → 5175`.
  - Override: `QUIZ_MANAGER_PORT`.
  - Compose files:
    `docker-compose.yml`, `app/flashoffer/docker/analytics.yml`,
    `app/flashoffer/docker/quiz.yml`.

- **campaign-manager**
  - Purpose: React + FastAPI admin for campaign metadata.
  - Host → container: `5174 → 4173`.
  - Override: `CAMPAIGN_MANAGER_PORT` (host side only).
  - Compose files:
    `docker-compose.yml`, `app/flashoffer/docker/analytics.yml`,
    `app/flashoffer/docker/quiz.yml`, `app/flashoffer/docker/campaign.yml`.

## Backend APIs

- **analytics-backend**
  - Purpose: Event ingestion API for analytics events.
  - Host → container: `8001 → 8000`.
  - Override: none (adjust via compose file if needed).
  - Compose files:
    `docker-compose.yml`, `app/flashoffer/docker/analytics.yml`.

- **quiz-backend**
  - Purpose: Quiz content API supporting quiz-manager and flashoffer.
  - Host → container: `8002 → 8000`.
  - Override: none (adjust via compose file if needed).
  - Compose files:
    `docker-compose.yml`, `app/flashoffer/docker/analytics.yml`,
    `app/flashoffer/docker/quiz.yml`.

- **campaign-backend**
  - Purpose: Campaign metadata API consumed by campaign-manager and flashoffer.
  - Host → container: *not exposed* (reachable on the Docker network only).
  - Override: not applicable.
  - Compose files:
    `docker-compose.yml`, `app/flashoffer/docker/analytics.yml`,
    `app/flashoffer/docker/quiz.yml`, `app/flashoffer/docker/campaign.yml`.

## Supporting Services

- **analytics-db**
  - Purpose: TimescaleDB instance for analytics workloads.
  - Host → container: `5433 → 5432`.
  - Override: none (adjust via compose file if needed).
  - Compose files:
    `docker-compose.yml`, `app/flashoffer/docker/analytics.yml`.

- **nginx-dev**
  - Purpose: Serves the built press site for local preview.
  - Host → container: `80 → 80`.
  - Override: edit `docker-compose.yml`.
  - Compose files: `docker-compose.yml`.

When introducing new services, pick unused host ports and update this document
so the team can avoid collisions across the shared development environment.
