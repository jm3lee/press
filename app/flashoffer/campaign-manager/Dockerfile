# syntax=docker/dockerfile:1.6
######################################################################
# Flashoffer campaign manager image
#
# Builds the React admin interface and packages the FastAPI backend
# that serves campaign management endpoints.
######################################################################

FROM node:20-slim AS frontend-deps
WORKDIR /workspace/frontend

COPY app/flashoffer/campaign-manager/package.json ./package.json
COPY app/flashoffer/campaign-manager/package-lock.json ./package-lock.json
RUN --mount=type=cache,target=/root/.npm,id=flashoffer-campaign-manager npm ci

FROM frontend-deps AS frontend-build

COPY app/flashoffer/campaign-manager/tsconfig.json ./tsconfig.json
COPY app/flashoffer/campaign-manager/tsconfig.node.json ./tsconfig.node.json
COPY app/flashoffer/campaign-manager/vite.config.ts ./vite.config.ts
COPY app/flashoffer/campaign-manager/index.html ./index.html
COPY app/flashoffer/campaign-manager/src ./src
COPY app/flashoffer/flashoffer-react ./flashoffer-react
RUN --mount=type=cache,target=/root/.npm,id=flashoffer-campaign-manager npm run build

FROM python:3.11-slim AS backend-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt,id=flashoffer-campaign-manager \
    --mount=type=cache,target=/var/lib/apt/lists,id=flashoffer-campaign-manager \
    apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev \
    && python -m venv "${VIRTUAL_ENV}" \
    && rm -rf /var/lib/apt/lists/*

COPY app/flashoffer/campaign-manager/backend/requirements.txt ./requirements.txt
COPY app/flashoffer/backend-common /backend-common
COPY app/shell/py/pie /tmp/pie

RUN --mount=type=cache,target=/root/.cache/pip,id=flashoffer-campaign-manager-pip \
    pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir /tmp/pie dominate flask loguru \
    && rm -rf /tmp/pie /backend-common

COPY app/flashoffer/campaign-manager/backend/campaign_manager ./campaign_manager
COPY --from=frontend-build /workspace/frontend/dist ./static

RUN python - <<'PY'
import secrets
from pathlib import Path

password = secrets.token_urlsafe(24)
output_dir = Path("campaign_manager")
output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / "admin_password").write_text(password + "\n", encoding="utf-8")
PY

ENV PORT=4173 \
    BACKEND_PORT=8000 \
    CAMPAIGN_MANAGER_SECRET_KEY=flashoffer-campaign-manager-secret \
    CAMPAIGN_MANAGER_STATIC_DIR=/app/static \
    CAMPAIGN_MANAGER_ADMIN_PASSWORD_FILE=/app/campaign_manager/admin_password

FROM frontend-deps AS dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/workspace/.venv \
    PATH="/workspace/.venv/bin:${PATH}" \
    BACKEND_PORT=8000 \
    PORT=4173 \
    VITE_DEV_SERVER_PORT=5174

WORKDIR /workspace/app

RUN --mount=type=cache,target=/var/cache/apt,id=flashoffer-campaign-manager-dev \
    --mount=type=cache,target=/var/lib/apt/lists,id=flashoffer-campaign-manager-dev \
    apt-get update \
    && apt-get install --no-install-recommends -y build-essential curl libpq-dev python3 python3-pip python3-venv \
    && python3 -m venv "${VIRTUAL_ENV}" \
    && rm -rf /var/lib/apt/lists/*

COPY app/flashoffer/campaign-manager/package.json ./package.json
COPY app/flashoffer/campaign-manager/package-lock.json ./package-lock.json
COPY --from=frontend-deps /workspace/frontend/node_modules ./node_modules
COPY app/flashoffer/campaign-manager/tsconfig.json ./tsconfig.json
COPY app/flashoffer/campaign-manager/tsconfig.node.json ./tsconfig.node.json
COPY app/flashoffer/campaign-manager/vite.config.ts ./vite.config.ts
COPY app/flashoffer/campaign-manager/index.html ./index.html
COPY app/flashoffer/campaign-manager/src ./src
COPY app/flashoffer/flashoffer-react ./flashoffer-react

COPY app/flashoffer/campaign-manager/backend ./backend
COPY app/flashoffer/backend-common ./backend-common
COPY app/shell/py/pie ./tmp/pie

RUN --mount=type=cache,target=/root/.cache/pip,id=flashoffer-campaign-manager-dev-pip \
    pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend/requirements.txt \
    && pip install --no-cache-dir ./tmp/pie dominate flask loguru \
    && rm -rf ./tmp

COPY app/flashoffer/campaign-manager/dev-entrypoint.sh /workspace/dev-entrypoint.sh
RUN chmod +x /workspace/dev-entrypoint.sh

EXPOSE 4173 5174

ENTRYPOINT ["/workspace/dev-entrypoint.sh"]

FROM backend-base AS prod

RUN --mount=type=cache,target=/var/cache/apt,id=flashoffer-campaign-manager-prod \
    --mount=type=cache,target=/var/lib/apt/lists,id=flashoffer-campaign-manager-prod \
    apt-get update \
    && apt-get install --no-install-recommends -y nginx-light gettext-base \
    && rm -rf /var/lib/apt/lists/*

COPY app/flashoffer/campaign-manager/nginx.conf /etc/nginx/conf.d/default.conf
COPY app/flashoffer/campaign-manager/start-production.sh /start-production.sh
RUN chmod +x /start-production.sh

EXPOSE 4173

ENTRYPOINT ["/start-production.sh"]
