######################################################################
# Analytics API image
#
# The analytics backend is a Flask application that serves reporting
# endpoints consumed by the admin UI. This multi-stage build assembles a
# reusable base image with Python dependencies and then derives separate
# development and production targets.
######################################################################

# Use the slim Python image to keep the base layer small while still
# providing the tooling required to install Python wheels.
FROM python:3.11-slim AS base

# Disable bytecode generation to reduce container filesystem churn and set
# defaults used by both the dev and prod entrypoints.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=analytics_backend.app:create_app \
    CORS_ALLOW_ORIGINS=

# Run the application from /app to match the runtime layout expected by
# the Flask CLI and unit tests.
WORKDIR /app

# Copy dependency manifests and shared PIE utilities first so Docker can
# reuse the layer when application code changes.
COPY app/analytics-backend/requirements.txt ./requirements.txt
COPY app/shell/py/pie /tmp/pie

# Install application dependencies, the shared PIE package, and dominate
# (used to render HTML emails). Cleaning the temporary directory avoids
# keeping duplicate source trees in the final image.
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir /tmp/pie dominate \
    && rm -rf /tmp/pie

# Copy the application and tests as the final step so source edits only
# invalidate the top layer.
COPY app/analytics-backend/analytics_backend ./analytics_backend
COPY app/analytics-backend/tests ./tests

FROM base AS dev

# The development target exposes Flask's default port for the live reload
# server.
EXPOSE 8000

# Run the Flask development server by default to support local workflows.
CMD ["flask", "--app", "analytics_backend.app:create_app", "run", "--host=0.0.0.0", "--port=8000"]

FROM base AS prod

# Configure Gunicorn defaults; these can be overridden at runtime but the
# baked-in values match our deployment needs.
ENV GUNICORN_WORKERS=4 \
    GUNICORN_BIND=unix:/tmp/gunicorn.sock

# Install nginx for reverse proxying and clean up apt metadata to keep the
# image size in check.
RUN apt-get update \
    && apt-get install --no-install-recommends -y nginx \
    && rm -rf /var/lib/apt/lists/*

# Gunicorn is only required in the production image, so install it here to
# avoid bloating the base stage.
RUN pip install --no-cache-dir gunicorn

# Provide the templated nginx config and startup script used in
# deployments.
COPY app/analytics-backend/nginx.conf /etc/nginx/conf.d/default.conf
COPY app/analytics-backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# The production container serves the app via nginx on port 8000.
EXPOSE 8000

# Launch the entrypoint that supervises both nginx and Gunicorn.
CMD ["/entrypoint.sh"]
