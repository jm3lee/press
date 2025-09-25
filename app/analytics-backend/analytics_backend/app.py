"""Flask application providing an ingestion API for analytics events."""

from __future__ import annotations

import atexit
import json
import os
from typing import Any, Dict, Iterable, Set

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
    storage = TimescaleDB(config)
    storage.initialize()
    atexit.register(storage.close)
    app.config["DB_POOL"] = storage

    allowed_origins: Set[str] = {
        origin.strip()
        for origin in os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
        if origin.strip()
    }

    def apply_cors(response: Response) -> Response:
        if allowed_origins:
            origin = request.headers.get("Origin")
            if origin and ("*" in allowed_origins or origin in allowed_origins):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                vary = response.headers.get("Vary")
                if vary:
                    vary_values = {value.strip() for value in vary.split(",")}
                    if "Origin" not in vary_values:
                        response.headers["Vary"] = f"{vary}, Origin"
                else:
                    response.headers["Vary"] = "Origin"
            response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type")
            response.headers.setdefault(
                "Access-Control-Allow-Methods", "GET,POST,OPTIONS"
            )
            response.headers.setdefault("Access-Control-Max-Age", "3600")
        return response

    @app.after_request
    def add_cors_headers(response: Response) -> Response:  # pragma: no cover - flask
        return apply_cors(response)

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


__all__ = ["create_app"]
