"""Flask application providing an ingestion API for quiz events."""

from __future__ import annotations

import atexit
import json
import time
from typing import Any, Dict

from flask import Flask, Response, jsonify, request

from pie.logging import logger

from backend_common import DatabaseConfig, configure_cors

from .db import QuizResultsStore


HEALTHCHECK_QUERY = "SELECT 1 -- confirm quiz database connectivity"


def _coerce_bool(value: Any, *, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if value in {0, 1}:
            return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    raise ValueError(f"Field '{field}' must be a boolean value")


def _load_quiz_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    required = {"quiz_id", "user_id", "event_type"}
    missing = required - payload.keys()
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Missing required keys: {missing_list}")

    event_type = str(payload["event_type"]).strip().lower()
    if event_type != "complete":
        raise ValueError(f"Unsupported quiz event type: {payload['event_type']}")

    passed = _coerce_bool(payload.get("passed"), field="passed")

    metadata = payload.get("metadata") or payload.get("payload") or {}
    if not isinstance(metadata, dict):
        raise ValueError("'metadata' must be a JSON object when provided")

    attempt_id = payload.get("attempt_id")
    if attempt_id is not None:
        attempt_id = str(attempt_id)

    details = dict(metadata)
    if payload.get("score") is not None:
        details["score"] = payload["score"]
    if payload.get("duration_seconds") is not None:
        details["duration_seconds"] = payload["duration_seconds"]
    details["passed"] = passed

    return {
        "quiz_id": str(payload["quiz_id"]),
        "user_id": str(payload["user_id"]),
        "attempt_id": attempt_id,
        "occurred_at": payload.get("occurred_at"),
        "attempts": 1,
        "passes": 1 if passed else 0,
        "fails": 0 if passed else 1,
        "payload": details,
    }


def create_app() -> Flask:
    """Create and configure the Flask application instance."""

    app = Flask(__name__)

    config = DatabaseConfig.from_env()
    storage = _initialise_storage(app, config)
    atexit.register(storage.close)
    app.config["DB_POOL"] = storage

    apply_cors = configure_cors(app, component="quiz-backend")

    @app.route("/api/events/quiz", methods=["OPTIONS"])
    def quiz_options() -> Response:
        return apply_cors(Response(status=204))

    @app.route("/health", methods=["GET"])
    def healthcheck() -> Response:
        with storage.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(HEALTHCHECK_QUERY)
                cur.fetchone()
        return jsonify({"status": "ok"})

    @app.route("/api/events/quiz", methods=["POST"])
    def ingest_quiz_event() -> Response:
        if not request.data:
            return jsonify({"error": "request body required"}), 400

        try:
            payload = request.get_json(force=True)
        except Exception as exc:  # noqa: BLE001 - propagate error context
            return jsonify({"error": f"invalid JSON payload: {exc}"}), 400

        if not isinstance(payload, dict):
            return jsonify({"error": "payload must be a JSON object"}), 400

        try:
            result = _load_quiz_payload(payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        record = storage.record_completion(result)
        return jsonify({"result": record}), 201

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

    return app


def _initialise_storage(app: Flask, config: DatabaseConfig) -> QuizResultsStore:
    retry_interval = 5.0
    timeout = 300.0
    start_time = time.monotonic()
    deadline = start_time + timeout
    attempt = 1

    storage_logger = logger.bind(
        component="quiz-backend",
        operation="database-initialisation",
        flask_app=app.name,
    )

    while True:
        storage: QuizResultsStore | None = None
        try:
            storage = QuizResultsStore(config)
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
