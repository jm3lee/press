######################################################################
# Quiz API image
#
# The quiz backend ingests quiz completion events and stores aggregate
# tallies for reporting. This multi-stage build mirrors the analytics
# backend image so the two services can share operational tooling.
######################################################################

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=quiz_backend.app:create_app \
    CORS_ALLOW_ORIGINS=

WORKDIR /app

COPY app/quiz-backend/requirements.txt ./requirements.txt
COPY app/backend-common/backend_common ./backend_common
COPY app/shell/py/pie /tmp/pie

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir /tmp/pie dominate \
    && rm -rf /tmp/pie

COPY app/quiz-backend/quiz_backend ./quiz_backend
COPY app/quiz-backend/tests ./tests

FROM base AS dev

EXPOSE 8000

CMD ["flask", "--app", "quiz_backend.app:create_app", "run", "--host=0.0.0.0", "--port=8000"]

FROM base AS prod

ENV GUNICORN_WORKERS=4 \
    GUNICORN_BIND=unix:/tmp/gunicorn.sock

RUN apt-get update \
    && apt-get install --no-install-recommends -y nginx \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir gunicorn

COPY app/quiz-backend/nginx.conf /etc/nginx/conf.d/default.conf
COPY app/quiz-backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
