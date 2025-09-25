"""Flask application providing an ingestion API for analytics events."""

from __future__ import annotations

import atexit
import json
from typing import Any, Dict, Iterable

from flask import Flask, Response, jsonify, request

from .db import DatabaseConfig, TimescaleDB


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
        for key in ("event_type", "target"):
            if key not in event:
                raise ValueError(f"Missing '{key}' in event #{index}")
        normalised.append(event)
    return normalised


def create_app() -> Flask:
    """Create and configure the Flask application instance."""

    app = Flask(__name__)

    config = DatabaseConfig.from_env()
    storage = TimescaleDB(config)
    storage.initialize()
    atexit.register(storage.close)
    app.config["DB_POOL"] = storage

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


__all__ = ["create_app"]
