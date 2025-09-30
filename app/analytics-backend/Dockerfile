FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=analytics_backend.app:create_app \
    CORS_ALLOW_ORIGINS=

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY analytics_backend ./analytics_backend

FROM base AS dev
COPY tests ./tests

EXPOSE 8000

CMD ["flask", "--app", "analytics_backend.app:create_app", "run", "--host=0.0.0.0", "--port=8000"]

FROM base AS production
ENV GUNICORN_WORKERS=4 \
    GUNICORN_BIND=unix:/tmp/gunicorn.sock

RUN apt-get update \
    && apt-get install --no-install-recommends -y nginx \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir gunicorn

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
