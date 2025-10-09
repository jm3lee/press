"""Flask application serving campaign countdown metadata."""

from __future__ import annotations

import atexit
import json
import time
from datetime import datetime, timezone

from flask import Flask, Response, jsonify, request

from pie.logging import logger

from backend_common import DatabaseConfig, configure_cors

from .db import CampaignStore


def create_app() -> Flask:
    """Create and configure the Flask application."""

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
        return apply_cors(jsonify({"status": "ok"}))

    @app.route("/api/campaign/<campaign_id>/time_remaining", methods=["OPTIONS"])
    def time_remaining_options(campaign_id: str) -> Response:  # noqa: D401 - CORS helper
        return apply_cors(Response(status=204))

    @app.route("/api/campaign/<campaign_id>/time_remaining", methods=["GET"])
    def time_remaining(campaign_id: str) -> Response:
        record = storage.fetch_time_remaining(campaign_id)
        requested_campaign = request.args.get("cid", campaign_id)
        source = request.args.get("ct", "countdown-timer")

        if record is None:
            payload = {
                "campaign_id": requested_campaign,
                "time_remaining_ms": 0,
                "quantity_remaining": None,
                "source": source,
            }
            response = jsonify(payload)
            response.status_code = 404
            return apply_cors(response)

        payload = {
            "campaign_id": requested_campaign,
            "time_remaining_ms": record["time_remaining_ms"],
            "quantity_remaining": record["quantity_remaining"],
            "source": source,
            "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        return apply_cors(jsonify(payload))

    @app.route("/config", methods=["GET"])
    def config_dump() -> Response:
        details = {
            "database": {
                "host": config.host,
                "port": config.port,
                "name": config.database,
            }
        }
        return apply_cors(Response(json.dumps(details), mimetype="application/json"))

    return app


def _initialise_storage(app: Flask, config: DatabaseConfig) -> CampaignStore:
    """Initialise the campaign store with retry semantics."""

    retry_interval = 5.0
    timeout = 300.0
    start_time = time.monotonic()
    deadline = start_time + timeout
    attempt = 1

    storage_logger = logger.bind(
        component="campaign-backend",
        operation="database-initialisation",
        flask_app=app.name,
    )

    while True:
        storage: CampaignStore | None = None
        try:
            storage = CampaignStore(config)
            storage.initialize()
            storage.ensure_demo_campaign()
        except Exception as exc:  # noqa: BLE001 - preserve original context
            if storage is not None:
                try:
                    storage.close()
                except Exception:  # noqa: BLE001 - suppress during cleanup
                    pass

            now = time.monotonic()
            if now >= deadline:
                storage_logger.opt(exception=exc).error(
                    "Failed to connect to the database",
                    attempts=attempt,
                    timeout_seconds=timeout,
                    elapsed_seconds=now - start_time,
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
                elapsed_seconds=time.monotonic() - start_time,
            )
            return storage


__all__ = ["create_app"]
