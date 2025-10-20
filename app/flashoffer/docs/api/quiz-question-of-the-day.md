# Quiz Question of the Day Endpoint

The `/api/quiz/today` route exposes the currently active marketing quiz
question. Clients poll the endpoint to hydrate homepage placements, in-product
nudges, and notification copy. Every response is derived from the
`quiz_questions` table that content managers populate through the authoring
interfaces or ingestion API.

## Where the Entry Comes From

Quiz questions are persisted via `POST /api/quiz/questions` and stored with
their publication metadata. The quiz backend records the canonical fields for
each question: a unique slug, prompt text, optional helper copy, answer choices
(as JSON), and the identifier of the correct option. Two date columns schedule
the question:

- `published_on` — the first day the question becomes eligible for rotation.
- `expires_on` — an optional retirement date. Null means the question remains
  active indefinitely.

Whenever `/api/quiz/today` is called, the service asks the `QuizResultsStore`
for the question of the day. The store performs a parameterized query against
the Postgres table. The SQL lives in
`quiz_backend/sql/fetch_question_of_day.sql`:

```
SELECT
    id,
    slug,
    question,
    helper_text,
    explanation,
    success_message,
    error_message,
    options,
    correct_option_id,
    published_on,
    expires_on
FROM quiz_questions
WHERE published_on <= %s
  AND (expires_on IS NULL OR expires_on > %s)
ORDER BY published_on DESC, id DESC
LIMIT 1
```

The placeholders are bound to the current date in Coordinated Universal Time.
A question is returned only if it is already published and has not expired. The
`ORDER BY` clause ensures the most recently published record wins when multiple
entries satisfy the window.

## Response Payload

When the query finds a match, the backend serializes it into a stable schema
and wraps it in a JSON envelope:

```
{
  "question": {
    "id": 42,
    "slug": "flashoffer-demo",
    "question": "Which follow-up sustains conversion lift?",
    "helper_text": "Think about friction-free follow-ups.",
    "explanation": "Reminders reinforce urgency without blockers.",
    "success_message": "Exactly. Reinforce urgency to keep momentum.",
    "error_message": "Consider what keeps prospects moving forward.",
    "options": [
      {"id": "reminder", "label": "Send a reminder"},
      {"id": "delay", "label": "Delay outreach"}
    ],
    "correct_option_id": "reminder",
    "published_on": "2024-09-01",
    "expires_on": null
  }
}
```

The `options` array is emitted exactly as stored, allowing channel-specific
renderers to show labels, descriptions, or other metadata that authoring tools
attach. Timestamps such as `published_on` and `expires_on` are formatted using
ISO-8601 strings. Internal audit fields (`created_at`, `updated_at`) stay
private to reduce payload size.

## Failure Modes

If no question satisfies the date filters, the route returns
`404 Not Found` with `{ "error": "question_not_available" }`. This commonly
occurs when content has not yet been scheduled for the day or has just expired.
Applications should handle the 404 by hiding quiz surfaces or falling back to a
campaign-specific experience.
