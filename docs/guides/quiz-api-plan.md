# Quiz API Implementation Plan

## Objective

Create a new Flask-based service at `app/quiz-api` modeled on the existing
`app/analytics-backend` project. The service will process quiz analytics events
and persist quiz completion statistics.

## Milestones

1. **Project Bootstrap**
   - Copy the project structure from `app/analytics-backend`, adapting package
     names and entry points to `quiz_api`.
   - Update `Dockerfile`, `entrypoint.sh`, and `requirements.txt` to reflect the
     new service name.
   - Ensure application factory (`create_app`) lives under
     `app/quiz-api/quiz_api/app.py` and imports from a local `db.py` module.

2. **HTTP API**
   - Expose a POST endpoint at `/api/events/quiz` to receive quiz events.
   - Accept JSON payloads with metadata similar to the analytics backend. Enforce
     schema validation: require `site`, `session_id`, and an `events` list.
   - Support the quiz event type `complete`. Reject unsupported event types with
     a `400` response explaining the issue.
   - Reuse CORS handling, health check, and configuration endpoints from the
     reference service.

3. **Database Layer**
   - Add a `quiz_attempts` table with columns for `site`, `session_id`,
     `quiz_id`, `completed_at`, `passed`, and `metadata`. Choose TimescaleDB
     hypertable conventions if time-series queries are needed, mirroring the
     existing schema style.
   - Extend the DB helper to ensure the table exists on startup and to insert
     quiz completion rows in a single transaction.
   - Ensure the `passed` flag is derived from the incoming event metadata
     (`meta["passed"]`) and default to `FALSE` when absent.

4. **Event Processing Logic**
   - When a `complete` event arrives, persist a new quiz attempt row, incrementing
     internal counters for attempts, passes, and failures. Calculate these totals
     by updating aggregate columns or returning derived counts from the insert
     result.
   - Decide whether to perform aggregation in SQL (e.g., using `ON CONFLICT` and
     incrementing counters) or in Python with separate queries, documenting the
     choice.
   - Return a JSON payload confirming the recorded attempt and providing the
     updated attempt/pass/fail tallies for the quiz and site combination.

5. **Testing**
   - Mirror analytics backend tests to cover payload validation, event routing,
     and database interactions (use a temporary PostgreSQL instance or mocks).
   - Add tests verifying that attempts, passes, and failures increment correctly
     after multiple `complete` events with varying `passed` values.
   - Cover health check, configuration endpoint, and CORS headers.

6. **Operations**
   - Wire the service into docker-compose or deployment tooling if required,
     ensuring environment variables for database connectivity are documented.
   - Provide README updates describing API usage, request/response formats, and
     database schema migrations.
   - Add monitoring/logging hooks consistent with existing backend services.
