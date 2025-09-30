FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY app/analytics-backend/requirements.txt ./requirements.txt
COPY app/shell/py/pie /tmp/pie
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir /tmp/pie \
    && rm -rf /tmp/pie

COPY app/analytics-backend/analytics_backend ./analytics_backend
COPY app/analytics-backend/tests ./tests

ENV FLASK_APP=analytics_backend.app:create_app \
    CORS_ALLOW_ORIGINS=

EXPOSE 8000

CMD ["flask", "--app", "analytics_backend.app:create_app", "run", "--host=0.0.0.0", "--port=8000"]
