# Quiz Backend Architecture

## Overview
The quiz backend is a Flask application that exposes REST endpoints for quiz
question management, daily quiz publishing, and completion telemetry. It relies
on the shared `backend-common` package for database configuration, connection
pooling, and CORS support. The service ships inside the `press-quiz-backend`
image and runs behind an embedded Nginx proxy that terminates HTTP and forwards
requests to Gunicorn workers.

## Process Model
`entrypoint.sh` starts Gunicorn with four workers bound to a Unix domain socket
and launches Nginx in the same container. Nginx listens on port 8000 as defined
in `nginx.conf` and proxies traffic to `/tmp/gunicorn.sock`, adding the standard
forwarded headers expected by upstream load balancers. The entrypoint cleans up
both processes and the socket when the container stops, keeping restarts
idempotent.

## Application Setup
`create_app()` instantiates Flask, loads connection settings from environment
variables via `DatabaseConfig.from_env()`, and initialises the Postgres-backed
`QuizResultsStore`. Startup blocks until the database is reachable, retrying for
up to five minutes. Once connected, the store is cached in
`app.config['DB_POOL']`, and the `configure_cors()` helper attaches permissive
responses to every quiz route. A process exit handler closes the connection pool
gracefully.

## Data Storage Layer
`QuizResultsStore` extends the shared `PostgresPool` helper. During
initialisation it executes SQL migrations shipped in `quiz_backend/sql/` to
create the results and questions tables plus supporting indexes. The store
provides typed methods:

- `record_completion()` – Normalises event payloads, casts tallies, and inserts
  rows via `INSERT_QUIZ_RESULT_SQL`, returning the stored record.
- `fetch_recent_results()` – Queries recent completions with campaign filters
  and bounded pagination.
- `create_question()` and `update_question()` – Validate publication windows,
  persist question metadata, and return the new or updated row.
- `list_questions()` and `fetch_question_of_day()` – List catalog entries or
  materialise the currently published question.

Helper routines such as `_parse_date()` and `_parse_timestamp()` ensure ISO
strings map cleanly to database types.

## HTTP Endpoints
The application defines a REST surface rooted at `/api/quiz/`:

- `/api/quiz/events` accepts POSTed completion events, validating required keys
  and enforcing a `event_type == "complete"` contract. The GET variant
  paginates recent events.
- `/api/quiz/questions` supports GET, POST, and PUT (via
  `/api/quiz/questions/<slug>`) for listing, creating, and updating question
  payloads. Requests pass through `_load_question_payload()` to guarantee slug,
  option, and date integrity.
- `/api/quiz/questions/generate` proxies to OpenAI when `OPENAI_API_KEY` is set.
  It constructs a deterministic system prompt, validates the user prompt, and
  returns both the normalised question and the raw model response.
- `/api/quiz/today` returns the active question of the day or `404` when none is
  scheduled.
- `/health` runs a lightweight `SELECT 1` probe against Postgres.
- `/config` surfaces database connection metadata for diagnostic tooling.

Every mutating route returns explicit error messages on validation failures and
logs server-side exceptions with structured context through `pie.logging`.

## External Integrations
The OpenAI client is optional: the module attempts to import `openai.OpenAI` at
runtime and short-circuits the generator endpoint when the dependency or API key
is missing. All outbound requests use `httpx.Client` instances configured with
component-specific timeouts. Because CORS support is enabled at initialisation,
the quiz manager frontend can call the backend directly during local
development and from hosted environments.
