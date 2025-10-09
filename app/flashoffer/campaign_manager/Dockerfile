# syntax=docker/dockerfile:1.6
######################################################################
# Flashoffer campaign manager image
#
# Builds the React admin interface and packages the FastAPI backend
# that serves campaign management endpoints.
######################################################################

FROM node:20-slim AS frontend-deps
WORKDIR /frontend

COPY app/flashoffer/campaign_manager/package.json ./package.json
COPY app/flashoffer/campaign_manager/package-lock.json ./package-lock.json
RUN --mount=type=cache,target=/root/.npm,id=flashoffer-campaign-manager npm ci

COPY app/flashoffer/campaign_manager/tsconfig.json ./tsconfig.json
COPY app/flashoffer/campaign_manager/tsconfig.node.json ./tsconfig.node.json
COPY app/flashoffer/campaign_manager/vite.config.ts ./vite.config.ts
COPY app/flashoffer/campaign_manager/index.html ./index.html
COPY app/flashoffer/campaign_manager/src ./src
COPY app/flashoffer/flashoffer-react ./flashoffer-react
RUN --mount=type=cache,target=/root/.npm,id=flashoffer-campaign-manager npm run build

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=4173 \
    CAMPAIGN_MANAGER_SECRET_KEY=flashoffer-campaign-manager-secret \
    CAMPAIGN_MANAGER_STATIC_DIR=/app/static \
    CAMPAIGN_MANAGER_ADMIN_PASSWORD_FILE=/workspace/app/flashoffer/campaign_manager/admin_password

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt,id=flashoffer-campaign-manager \
    --mount=type=cache,target=/var/lib/apt/lists,id=flashoffer-campaign-manager \
    apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY app/flashoffer/campaign_manager/backend/requirements.txt ./requirements.txt
COPY app/flashoffer/backend-common /backend-common

RUN --mount=type=cache,target=/root/.cache/pip,id=flashoffer-campaign-manager-pip \
    pip install --no-cache-dir -r requirements.txt

COPY app/flashoffer/campaign_manager/backend/campaign_manager ./campaign_manager
COPY --from=frontend-deps /frontend/dist ./static
COPY app/flashoffer/campaign_manager/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN python - <<'PY'
import secrets
from pathlib import Path
password = secrets.token_urlsafe(24)
output_dir = Path("/workspace/app/flashoffer/campaign_manager")
output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / "admin_password").write_text(password + "\n", encoding="utf-8")
PY

EXPOSE 4173

ENTRYPOINT ["/entrypoint.sh"]
