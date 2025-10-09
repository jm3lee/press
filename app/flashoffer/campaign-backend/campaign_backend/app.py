"""Flask application that exposes campaign deadline metadata."""

from __future__ import annotations

import atexit
import json
import time
from datetime import datetime, timezone

from flask import Flask, Response, jsonify

from pie.logging import logger

from backend_common import DatabaseConfig, configure_cors

from .db import CampaignStore


def _compute_remaining_ms(end_time: datetime) -> int:
    now = datetime.now(tz=timezone.utc)
    delta = end_time.astimezone(timezone.utc) - now
    return max(0, int(delta.total_seconds() * 1000))


def create_app() -> Flask:
    """Create and configure the campaign backend application."""

    app = Flask(__name__)

    config = DatabaseConfig.from_env()
    storage = _initialise_storage(app, config)
    atexit.register(storage.close)
    app.config["DB_POOL"] = storage

    apply_cors = configure_cors(app, component="campaign-backend")

    @app.route("/health", methods=["GET"])
    def healthcheck() -> Response:
        with storage.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return jsonify({"status": "ok"})

    @app.route("/config", methods=["GET"])
    def config_dump() -> Response:
        details = {
            "database": {
                "host": config.host,
                "port": config.port,
                "name": config.database,
            }
        }
        return Response(json.dumps(details), mimetype="application/json")

    @app.route("/api/campaign/<campaign_id>/end_time", methods=["OPTIONS"])
    def campaign_options(campaign_id: str) -> Response:  # noqa: D401 - CORS preflight
        return apply_cors(Response(status=204))

    @app.route("/api/campaign/<campaign_id>/end_time", methods=["GET"])
    def campaign_end_time(campaign_id: str) -> Response:
        campaign_id = campaign_id.strip()
        if not campaign_id:
            return apply_cors(
                jsonify({"error": "campaign id must be provided"}),
            ), 400

        record = storage.fetch_end_time(campaign_id)
        if record is None:
            return apply_cors(jsonify({"error": "campaign not found"})), 404

        payload = {
            "campaign_id": campaign_id,
            "end_time": record.astimezone(timezone.utc).isoformat(),
            "remaining_ms": _compute_remaining_ms(record),
        }
        return apply_cors(jsonify(payload))

    return app


def _initialise_storage(app: Flask, config: DatabaseConfig) -> CampaignStore:
    """Initialise the database connection with retry semantics."""

    retry_interval = 5.0
    timeout = 300.0
    start = time.monotonic()
    deadline = start + timeout
    attempt = 1

    storage_logger = logger.bind(
        component="campaign-backend",
        operation="database-initialisation",
        flask_app=app.name,
    )

    while True:
        store: CampaignStore | None = None
        try:
            store = CampaignStore(config)
            store.initialize()
        except Exception as exc:  # noqa: BLE001 - propagate context
            if store is not None:
                try:
                    store.close()
                except Exception:  # noqa: BLE001 - suppress cleanup errors
                    pass

            now = time.monotonic()
            if now >= deadline:
                storage_logger.opt(exception=exc).error(
                    "Failed to connect to the database",
                    attempts=attempt,
                    timeout_seconds=timeout,
                    elapsed_seconds=now - start,
                )
                raise

            storage_logger.opt(exception=exc).warning(
                "Database connection attempt failed",
                attempt=attempt,
                retry_interval_seconds=retry_interval,
                seconds_until_timeout=max(0.0, deadline - now),
            )
            attempt += 1
            time.sleep(retry_interval)
        else:
            storage_logger.info(
                "Connected to the database",
                attempts=attempt,
                elapsed_seconds=time.monotonic() - start,
            )
            return store


__all__ = ["create_app"]
