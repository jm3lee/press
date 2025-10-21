# Copyright (c) Flashoffer Developers
# Released under the MIT license.
"""Flask application providing an ingestion API for quiz events."""

from __future__ import annotations

import atexit
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

import httpx
from flask import Flask, Request, Response, jsonify, request

from pie.logging import logger

from backend_common import DatabaseConfig, configure_cors

from .db import QuizResultsStore

try:
    from openai import OpenAI  # type: ignore
except Exception:  # noqa: BLE001 - optional dependency
    OpenAI = None  # type: ignore[misc]


HEALTHCHECK_QUERY = "SELECT 1 -- confirm quiz database connectivity"

QUIZ_CELEBRATION_PRESETS = {
    "off",
    "classic",
    "streamers",
    "burst",
}


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

    celebration_value = payload.get("celebration")
    celebration = "off"
    if celebration_value is not None:
        celebration = str(celebration_value).strip() or "off"
    if celebration not in QUIZ_CELEBRATION_PRESETS:
        allowed = ", ".join(sorted(QUIZ_CELEBRATION_PRESETS))
        raise ValueError(
            f"Field 'celebration' must be one of: {allowed}"
        )

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
        "celebration": celebration,
    }


_DEFAULT_GENERATION_USER_PROMPT = (
    "Create a question about digital marketing measurement best practices."
)


class GenerationRequestError(ValueError):
    """Raised when an inbound generation request is invalid."""


class GenerationModelError(RuntimeError):
    """Raised when the OpenAI response cannot be converted into a question."""


@dataclass(frozen=True)
class GenerationRequest:
    """Validated parameters for generating a quiz question."""

    prompt: str
    model: str


def _build_generation_system_prompt() -> str:
    today = datetime.now(tz=timezone.utc).date().isoformat()
    return (
        "You are Flashoffer's quiz authoring assistant. "
        "Produce exactly one JSON object describing a multiple-choice quiz question. "
        "The JSON must NOT be wrapped in any additional words or Markdown. "
        "Structure the object with these keys: slug, question, helper_text, explanation, "
        "success_message, error_message, options, correct_option_id, published_on, expires_on. "
        "Rules: slug must be lowercase kebab-case (letters, digits, hyphen) with a maximum length of 48 characters. "
        "question should be concise plain text without HTML. "
        "Provide helper_text, explanation, success_message, and error_message when useful; otherwise use null. "
        "options must contain at least three entries. Each entry needs id (lowercase string), label (answer text), "
        "and optional description (<= 140 characters). "
        "Shuffle or randomize the placement of the correct option so it is not "
        "always first or predictably positioned. "
        "correct_option_id must exactly match one option id. "
        f"Use '{today}' for published_on unless instructed otherwise. "
        "Set expires_on to null unless a future ISO date is explicitly requested. "
        "Return valid JSON only, with proper escaping and no comments."
    )


def _derive_openai_base_url() -> str:
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    if not base_url.lower().startswith("https://"):
        raise ValueError("OpenAI base URL must use https")
    return base_url


def _initialise_openai_client(api_key: str) -> tuple["OpenAI", httpx.Client]:  # type: ignore[name-defined]
    base_url = _derive_openai_base_url()
    http_client = httpx.Client(
        follow_redirects=True,
        timeout=httpx.Timeout(60.0),
        trust_env=False,
    )
    client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)  # type: ignore[misc]
    return client, http_client


def _load_generation_payload(flask_request: Request) -> Dict[str, Any]:
    try:
        payload = flask_request.get_json(force=False, silent=True)
    except Exception as exc:  # noqa: BLE001 - propagate context for clients
        raise GenerationRequestError(f"invalid JSON payload: {exc}") from exc

    if payload is None:
        return {}

    if not isinstance(payload, dict):
        raise GenerationRequestError("payload must be a JSON object")

    return payload


def _parse_generation_request(flask_request: Request) -> GenerationRequest:
    payload = _load_generation_payload(flask_request)

    prompt_value = payload.get("prompt")
    if prompt_value is None:
        prompt = ""
    elif isinstance(prompt_value, str):
        prompt = prompt_value
    else:
        raise GenerationRequestError("prompt must be a string")

    model = str(payload.get("model") or "gpt-5").strip() or "gpt-5"

    return GenerationRequest(prompt=prompt, model=model)


def _request_generated_question(
    client: "OpenAI", *, model: str, prompt: str
) -> tuple[Dict[str, Any], Dict[str, Any]]:  # type: ignore[name-defined]
    system_prompt = _build_generation_system_prompt()
    user_prompt = prompt.strip() or _DEFAULT_GENERATION_USER_PROMPT

    completion = client.chat.completions.create(  # type: ignore[attr-defined]
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    try:
        content = completion.choices[0].message.content  # type: ignore[index]
    except Exception as exc:  # noqa: BLE001 - guard against SDK changes
        raise GenerationModelError(f"unexpected_openai_response: {exc}") from exc

    if not content:
        raise GenerationModelError("empty_completion")

    try:
        generated = json.loads(content)
    except json.JSONDecodeError as exc:
        raise GenerationModelError(f"invalid_json_from_model: {exc}") from exc

    if not isinstance(generated, dict):
        raise GenerationModelError("model_output_must_be_object")

    try:
        question_payload = _load_question_payload(generated)
    except ValueError as exc:
        raise GenerationModelError(f"model_output_invalid: {exc}") from exc

    return question_payload, generated


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
    quiz_question_detail_path = "/api/quiz/questions/<slug>"
    quiz_questions_generate_path = "/api/quiz/questions/generate"
    quiz_stats_path = "/api/quiz/stats/<slug>"

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

    @app.route(quiz_questions_generate_path, methods=["OPTIONS"])
    def quiz_questions_generate_options() -> Response:
        return apply_cors(Response(status=204))

    @app.route(quiz_question_detail_path, methods=["OPTIONS"])
    def quiz_question_detail_options(slug: str) -> Response:  # noqa: ARG001 - required by Flask
        return apply_cors(Response(status=204))

    @app.route(quiz_stats_path, methods=["OPTIONS"])
    def quiz_stats_options(slug: str) -> Response:  # noqa: ARG001 - required by Flask
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

    @app.route(quiz_stats_path, methods=["GET"])
    def quiz_stats(slug: str) -> Response:
        stats = storage.fetch_quiz_stats(slug)
        if stats is None:
            return jsonify({"error": "quiz_stats_not_found"}), 404
        return jsonify({"stats": stats})

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

    @app.route(quiz_questions_generate_path, methods=["POST"])
    def generate_quiz_question() -> Response:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({"error": "openai_api_key_missing"}), 503

        try:
            generation_request = _parse_generation_request(request)
        except GenerationRequestError as exc:
            return jsonify({"error": str(exc)}), 400

        if OpenAI is None:
            return jsonify({"error": "openai_client_not_available"}), 500

        managed_http_client: httpx.Client | None = None
        try:
            try:
                client, managed_http_client = _initialise_openai_client(api_key)
            except Exception as exc:
                logger.bind(component="quiz-backend", operation="ai-generate").exception(
                    "Failed to initialise OpenAI client"
                )
                return jsonify({"error": f"openai_client_init_failed: {exc}"}), 502

            try:
                question_payload, generated = _request_generated_question(
                    client,
                    model=generation_request.model,
                    prompt=generation_request.prompt,
                )
            except GenerationModelError as exc:
                return jsonify({"error": str(exc)}), 502
            except Exception as exc:  # noqa: BLE001 - surface API error
                logger.bind(component="quiz-backend", operation="ai-generate").exception(
                    "OpenAI request failed"
                )
                return jsonify({"error": f"openai_request_failed: {exc}"}), 502

            return jsonify({"question": question_payload, "raw": generated})
        finally:
            if managed_http_client is not None:
                managed_http_client.close()

    @app.route(quiz_question_detail_path, methods=["PUT"])
    def update_quiz_question(slug: str) -> Response:
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
            if question_payload["slug"] != slug:
                return jsonify({"error": "slug mismatch"}), 400
            record = storage.update_question(slug, question_payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            logger.bind(
                component="quiz-backend",
                operation="update-question",
                slug=slug,
            ).exception("Failed to update quiz question")
            return jsonify({"error": "failed_to_update_question"}), 500

        return jsonify({"question": record})

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
