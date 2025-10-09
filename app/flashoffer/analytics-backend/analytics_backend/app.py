"""Flask application providing an ingestion API for analytics events."""

from __future__ import annotations

import atexit
import json
import os
import time
from typing import Any, Dict, Iterable

from flask import Flask, Response, jsonify, request

from pie.logging import logger

from backend_common import DatabaseConfig, configure_cors

from .db import TimescaleDB


def _load_event_payload(payload: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    required = {"site", "session_id", "events"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Missing required keys: {', '.join(sorted(missing))}")

    events = payload["events"]
    if not isinstance(events, list) or not events:
        raise ValueError("'events' must be a non-empty list")

    normalised = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError(f"Event #{index} must be an object")
        if "target" not in event:
            raise ValueError(f"Missing 'target' in event #{index}")

        event_type = event.get("event_type") or event.get("type")
        if not event_type:
            raise ValueError(f"Missing 'type' in event #{index}")

        occurred_at = event.get("occurred_at") or event.get("at")

        meta = event.get("meta", {})
        if meta is None:
            meta = {}
        if not isinstance(meta, dict):
            raise ValueError(f"'meta' must be an object in event #{index}")

        normalised.append(
            {
                "event_type": str(event_type),
                "target": str(event["target"]),
                "occurred_at": occurred_at,
                "meta": meta,
            }
        )
    return normalised


def create_app() -> Flask:
    """Create and configure the Flask application instance."""

    app = Flask(__name__)

    config = DatabaseConfig.from_env()
    storage = _initialise_storage(app, config)
    atexit.register(storage.close)
    app.config["DB_POOL"] = storage

    apply_cors = configure_cors(app, component="analytics-backend")

    @app.route("/events", methods=["OPTIONS"])
    @app.route("/events/recent", methods=["OPTIONS"])
    def options_handler() -> Response:
        return apply_cors(Response(status=204))

    @app.route("/health", methods=["GET"])
    def healthcheck() -> Response:
        with storage.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return jsonify({"status": "ok"})

    @app.route("/events", methods=["POST"])
    def ingest_events() -> Response:
        if not request.data:
            return jsonify({"error": "request body required"}), 400

        try:
            payload = request.get_json(force=True)
        except Exception as exc:  # noqa: BLE001 - propagate error context
            return jsonify({"error": f"invalid JSON payload: {exc}"}), 400

        if not isinstance(payload, dict):
            return jsonify({"error": "payload must be a JSON object"}), 400

        try:
            events = list(_load_event_payload(payload))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        inserted = storage.insert_events(
            site=payload["site"],
            session_id=payload["session_id"],
            events=events,
        )
        return jsonify({"inserted": inserted}), 201

    @app.route("/events/recent", methods=["GET"])
    def recent_events() -> Response:
        try:
            limit = int(request.args.get("limit", "25"))
        except ValueError:
            limit = 25
        limit = max(1, min(limit, 200))
        events = storage.fetch_recent_events(limit)
        return jsonify({"events": events})

    @app.route("/config", methods=["GET"])
    def config_dump() -> Response:
        """Return a limited subset of runtime configuration."""

        details = {
            "database": {
                "host": config.host,
                "port": config.port,
                "name": config.database,
            }
        }
        return Response(json.dumps(details), mimetype="application/json")

    return app


def _initialise_storage(app: Flask, config: DatabaseConfig) -> TimescaleDB:
    """Initialise the database connection with retry semantics."""

    retry_interval = 5.0
    timeout = 300.0
    start_time = time.monotonic()
    deadline = start_time + timeout
    attempt = 1

    storage_logger = logger.bind(
        component="analytics-backend",
        operation="database-initialisation",
        flask_app=app.name,
    )

    while True:
        storage: TimescaleDB | None = None
        try:
            storage = TimescaleDB(config)
            storage.initialize()
        except Exception as exc:  # noqa: BLE001 - must propagate original error
            if storage is not None:
                try:
                    storage.close()
                except Exception:  # noqa: BLE001 - suppress during retry cleanup
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
