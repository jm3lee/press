# syntax=docker/dockerfile:1.7
######################################################################
# Quiz API image
#
# The quiz backend ingests quiz completion events and stores aggregate
# tallies for reporting. This multi-stage build mirrors the analytics
# backend image so the two services can share operational tooling.
######################################################################

FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=quiz_backend.app:create_app \
    CORS_ALLOW_ORIGINS=

WORKDIR /app

COPY app/flashoffer/quiz-backend/requirements.txt ./requirements.txt
COPY app/flashoffer/quiz-backend/requirements-dev.txt ./requirements-dev.txt
COPY app/flashoffer/backend-common /backend-common
COPY app/shell/py/pie /tmp/pie

# Maintenance: dedicate a pip cache to the quiz image so
# concurrent builds stay independent from the analytics cache
# and avoid file-lock conflicts.
# Install application dependencies, the shared PIE package, and
# dominate to support HTML email rendering. Cleaning the temporary
# directory avoids keeping duplicate source trees in the final image.
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -r requirements.txt \
    && pip install /tmp/pie dominate \
    && rm -rf /tmp/pie /backend-common

COPY app/flashoffer/quiz-backend/quiz_backend ./quiz_backend

# Defer copying tests to dev-oriented stages so production images exclude them.

FROM base AS dev
WORKDIR /app

# Ensure pytest and the other dev dependencies are present for local workflows
# that execute within the dev image.
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -r requirements-dev.txt

EXPOSE 8000

# Surface the quiz test suite for local workflows executed inside the dev image.
COPY app/flashoffer/quiz-backend/tests ./tests

CMD ["flask", "--app", "quiz_backend.app:create_app", "run", "--host=0.0.0.0", "--port=8000"]

FROM base AS prod

ENV GUNICORN_WORKERS=4 \
    GUNICORN_BIND=unix:/tmp/gunicorn.sock

# Install nginx for reverse proxying and keep apt metadata cached during
# builds to speed up rebuilds without bloating the runtime image.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update \
    && apt-get install --no-install-recommends -y nginx \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install gunicorn

COPY app/flashoffer/quiz-backend/nginx.conf /etc/nginx/conf.d/default.conf
COPY app/flashoffer/quiz-backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
