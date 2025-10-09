# Flashoffer Campaign Manager

The campaign manager pairs a React dashboard with a FastAPI backend so growth
marketers can create, edit, and monitor Flashoffer promotions without touching
application code. The UI consumes the backend through the same `/api` contract
that production services expose, making it a faithful representation of the
live environment.

## Architecture overview

The service ships as a multi-stage Docker build with three primary concerns:

- **Frontend build** – Vite compiles the React dashboard and bundles the
  `flashoffer-react` component library for production delivery.
- **Backend base** – A Python 3.11 environment packages the FastAPI
  application, preloads dependencies from `backend-common`, and generates the
  administrator password during image creation.
- **Production runtime** – Nginx serves the compiled React assets and reverse
  proxies API traffic to Uvicorn. Static assets live under `/app/static` while
  the backend listens on port `8000` and remains internal to the container.

The backend persists campaign metadata in PostgreSQL via `CampaignRepository`.
Analytics requests are proxied to the Flashoffer analytics backend and surfaced
in the dashboard through the `EventConsole` component.

## Local development

Use the `dev` stage in the Dockerfile to start both the FastAPI backend and the
Vite development server with hot reload enabled. The stage installs Node.js,
Python tooling, and project dependencies in a reproducible environment. Launch
it with Docker Compose or a direct `docker build`/`docker run` sequence:

```bash
docker build \
  --target dev \
  -t flashoffer-campaign-manager-dev \
  -f app/flashoffer/campaign-manager/Dockerfile \
  .

docker run --rm -p 5174:5174 -p 4173:4173 flashoffer-campaign-manager-dev
```

The container exposes the Vite server on port `5174` and proxies API requests
at `http://localhost:4173/api`. File changes trigger instantaneous reloads for
both the backend (through Uvicorn's watch mode) and the frontend (through Vite).

## Production deployment

Build the production stage to obtain an image that serves the dashboard via
Nginx while running Uvicorn in the background:

```bash
docker build \
  --target production \
  -t flashoffer-campaign-manager \
  -f app/flashoffer/campaign-manager/Dockerfile \
  .

docker run --rm -p 4173:4173 flashoffer-campaign-manager
```

Nginx listens on port `4173` by default and rewrites unknown routes to
`index.html` so React Router can handle client-side navigation. Override the
`PORT` or `BACKEND_PORT` environment variables at runtime if the host requires
custom bindings.

### API authentication

The image generates an administrator password during build time and stores it in
`/app/campaign_manager/admin_password`. Retrieve the credential with the helper
script `bin/campaign-manager-admin-password` or by inspecting the file directly
from a running container:

```bash
docker compose run --entrypoint cat campaign-manager \
  /app/campaign_manager/admin_password
```

Keep the password secret and rotate the image whenever long-lived credentials
are suspected of exposure.
