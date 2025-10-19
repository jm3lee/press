# syntax=docker/dockerfile:1.7
######################################################################
# Campaign API image
#
# The campaign backend serves countdown metadata for Flashoffer demos.
# This build mirrors other Flashoffer services so operations teams can
# reuse deployment runbooks across analytics, quiz, and campaign APIs.
######################################################################

FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=campaign_backend.app:create_app \
    CORS_ALLOW_ORIGINS=

WORKDIR /app

COPY app/flashoffer/campaign-backend/requirements.txt ./requirements.txt
COPY app/flashoffer/campaign-backend/requirements-dev.txt ./requirements-dev.txt
COPY app/flashoffer/backend-common /backend-common
COPY app/shell/py/pie /tmp/pie

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -r requirements.txt \
    && pip install /tmp/pie dominate \
    && rm -rf /tmp/pie /backend-common

COPY app/flashoffer/campaign-backend/campaign_backend ./campaign_backend

# Tests live in dev-oriented stages so the production image stays lean.

FROM base AS dev

# Install the dev requirements so pytest and related tooling stay available in
# local workflows that execute commands inside this image.
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -r requirements-dev.txt

EXPOSE 8000

# Provide the test suite for developers running pytest inside this target.
COPY app/flashoffer/campaign-backend/tests ./tests

CMD ["flask", "--app", "campaign_backend.app:create_app", "run", "--host=0.0.0.0", "--port=8000"]

FROM base AS prod

ENV GUNICORN_WORKERS=4 \
    GUNICORN_BIND=unix:/tmp/gunicorn.sock

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update \
    && apt-get install --no-install-recommends -y nginx \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install gunicorn

COPY app/flashoffer/campaign-backend/nginx.conf /etc/nginx/conf.d/default.conf
COPY app/flashoffer/campaign-backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
