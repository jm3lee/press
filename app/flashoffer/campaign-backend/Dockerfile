# syntax=docker/dockerfile:1.6
######################################################################
# Campaign API image
#
# The campaign backend exposes countdown metadata for Flashoffer timers.
# This multi-stage build mirrors the analytics and quiz services so the
# development workflow remains consistent across backend components.
######################################################################

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=campaign_backend.app:create_app \
    CORS_ALLOW_ORIGINS=

WORKDIR /app

COPY app/flashoffer/campaign-backend/requirements.txt ./requirements.txt
COPY app/flashoffer/backend-common /backend-common
COPY app/shell/py/pie /tmp/pie

RUN --mount=type=cache,target=/root/.cache/pip,id=campaign-backend-pip \
    pip install -r requirements.txt \
    && pip install /tmp/pie dominate \
    && rm -rf /tmp/pie /backend-common

COPY app/flashoffer/campaign-backend/campaign_backend ./campaign_backend
COPY app/flashoffer/campaign-backend/tests ./tests

FROM base AS dev

EXPOSE 8000

CMD ["flask", "--app", "campaign_backend.app:create_app", "run", "--host=0.0.0.0", "--port=8000"]

FROM base AS prod

ENV GUNICORN_WORKERS=4 \
    GUNICORN_BIND=unix:/tmp/gunicorn.sock

RUN --mount=type=cache,target=/var/cache/apt,id=campaign-backend \
    --mount=type=cache,target=/var/lib/apt/lists,id=campaign-backend \
    apt-get update \
    && apt-get install --no-install-recommends -y nginx \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip,id=campaign-backend-pip \
    pip install gunicorn

COPY app/flashoffer/campaign-backend/nginx.conf /etc/nginx/conf.d/default.conf
COPY app/flashoffer/campaign-backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
