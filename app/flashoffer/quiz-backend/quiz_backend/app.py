# Copyright (c) Flashoffer Developers
# Released under the MIT license.

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

    campaign_id = payload.get("campaign_id")
    if campaign_id is not None:
        campaign_id = str(campaign_id).strip()
        if not campaign_id:
            campaign_id = None

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
        "campaign_id": campaign_id,
        "occurred_at": payload.get("occurred_at"),
        "attempts": 1,
        "passes": 1 if passed else 0,
        "fails": 0 if passed else 1,
        "payload": details,
    }


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _load_question_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    required = {"slug", "question", "options", "correct_option_id", "published_on"}
    missing = required - payload.keys()
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Missing required keys: {missing_list}")

    slug = str(payload["slug"]).strip()
    if not slug:
        raise ValueError("Field 'slug' cannot be empty")

    question = str(payload["question"]).strip()
    if not question:
        raise ValueError("Field 'question' cannot be empty")

    options_raw = payload["options"]
    if not isinstance(options_raw, list) or not options_raw:
        raise ValueError("Field 'options' must be a non-empty array")

    normalized_options: list[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, option in enumerate(options_raw):
        if not isinstance(option, dict):
            raise ValueError(f"Option at index {index} must be a JSON object")
        option_id_raw = option.get("id")
        option_id = str(option_id_raw).strip() if option_id_raw is not None else ""
        if not option_id:
            raise ValueError(f"Option at index {index} must include an 'id'")
        if option_id in seen_ids:
            raise ValueError(f"Duplicate option id '{option_id}' detected")
        seen_ids.add(option_id)
        normalized_option: Dict[str, Any] = dict(option)
        normalized_option["id"] = option_id
        if "label" in normalized_option and normalized_option["label"] is not None:
            normalized_option["label"] = str(normalized_option["label"]).strip()
        if "description" in normalized_option and normalized_option["description"] is not None:
            normalized_option["description"] = str(normalized_option["description"]).strip()
        normalized_options.append(normalized_option)

    correct_option_id = str(payload["correct_option_id"]).strip()
    if not correct_option_id:
        raise ValueError("Field 'correct_option_id' cannot be empty")
    if correct_option_id not in seen_ids:
        raise ValueError("Field 'correct_option_id' must match an option id")

    published_on = payload["published_on"]
    expires_on = payload.get("expires_on")
    expires_value = str(expires_on).strip() if isinstance(expires_on, str) else expires_on
    normalized_expires_on = expires_value if expires_value else None

    helper_text = _normalize_optional_text(payload.get("helper_text"))
    explanation = _normalize_optional_text(payload.get("explanation"))
    success_message = _normalize_optional_text(payload.get("success_message"))
    error_message = _normalize_optional_text(payload.get("error_message"))

    return {
        "slug": slug,
        "question": question,
        "helper_text": helper_text,
        "explanation": explanation,
        "success_message": success_message,
        "error_message": error_message,
        "options": normalized_options,
        "correct_option_id": correct_option_id,
        "published_on": published_on,
        "expires_on": normalized_expires_on,
    }


def create_app() -> Flask:
    """Create and configure the Flask application instance."""

    app = Flask(__name__)

    config = DatabaseConfig.from_env()
    storage = _initialise_storage(app, config)
    atexit.register(storage.close)
    app.config["DB_POOL"] = storage

    apply_cors = configure_cors(app, component="quiz-backend")

    quiz_events_path = "/api/quiz/events"
    quiz_question_today_path = "/api/quiz/today"
    quiz_questions_path = "/api/quiz/questions"

    @app.route(quiz_events_path, methods=["OPTIONS"])
    def quiz_options() -> Response:
        return apply_cors(Response(status=204))

    @app.route("/health", methods=["GET"])
    def healthcheck() -> Response:
        with storage.connection() as conn:  # type: ignore[assignment]
            with conn.cursor() as cur:
                cur.execute(HEALTHCHECK_QUERY)
                cur.fetchone()
        return jsonify({"status": "ok"})

    @app.route(quiz_events_path, methods=["POST"])
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

    @app.route(quiz_events_path, methods=["GET"])
    def list_quiz_events() -> Response:
        try:
            limit = int(request.args.get("limit", "25"))
        except (TypeError, ValueError):
            limit = 25
        limit = max(1, min(limit, 200))

        raw_campaign_id = request.args.get("campaign_id")
        campaign_id = raw_campaign_id.strip() if raw_campaign_id else None
        if campaign_id == "":
            campaign_id = None

        results = storage.fetch_recent_results(limit=limit, campaign_id=campaign_id)
        return jsonify({"results": results})

    @app.route(quiz_question_today_path, methods=["OPTIONS"])
    def quiz_question_today_options() -> Response:
        return apply_cors(Response(status=204))

    @app.route(quiz_question_today_path, methods=["GET"])
    def quiz_question_today() -> Response:
        question = storage.fetch_question_of_day()
        if question is None:
            return jsonify({"error": "question_not_available"}), 404
        return jsonify({"question": question})

    @app.route(quiz_questions_path, methods=["OPTIONS"])
    def quiz_questions_options() -> Response:
        return apply_cors(Response(status=204))

    @app.route(quiz_questions_path, methods=["GET"])
    def list_quiz_questions() -> Response:
        try:
            limit = int(request.args.get("limit", "50"))
        except (TypeError, ValueError):
            limit = 50

        try:
            offset = int(request.args.get("offset", "0"))
        except (TypeError, ValueError):
            offset = 0

        limit = max(1, min(limit, 200))
        offset = max(0, offset)

        questions = storage.list_questions(limit=limit, offset=offset)
        payload = {
            "questions": questions,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "count": len(questions),
            },
        }
        return jsonify(payload)

    @app.route(quiz_questions_path, methods=["POST"])
    def create_quiz_question() -> Response:
        if not request.data:
            return jsonify({"error": "request body required"}), 400

        try:
            payload = request.get_json(force=True)
        except Exception as exc:  # noqa: BLE001 - propagate error context
            return jsonify({"error": f"invalid JSON payload: {exc}"}), 400

        if not isinstance(payload, dict):
            return jsonify({"error": "payload must be a JSON object"}), 400

        try:
            question_payload = _load_question_payload(payload)
            record = storage.create_question(question_payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            logger.bind(
                component="quiz-backend",
                operation="create-question",
                slug=payload.get("slug"),
            ).exception("Failed to insert quiz question")
            return jsonify({"error": "failed_to_create_question"}), 500

        return jsonify({"question": record}), 201

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
