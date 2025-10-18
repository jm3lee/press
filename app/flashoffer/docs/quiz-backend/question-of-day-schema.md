# Quiz Question of the Day Schema

`quiz-backend` exposes `/api/quiz/today` so frontend clients can render the
daily multiple choice prompt. This document captures the storage schema the
service uses and the access patterns maintained by `quiz_backend.db`.

## Table: `quiz_questions`

- `id BIGSERIAL PRIMARY KEY` – surrogate identifier for internal joins.
- `slug TEXT UNIQUE NOT NULL` – stable identifier that doubles as the quiz id
  for analytics correlation.
- `question TEXT NOT NULL` – primary prompt rendered above the answer list.
- `helper_text TEXT` – optional copy that appears beneath the prompt.
- `explanation TEXT` – rationale surfaced after users submit an answer.
- `success_message TEXT` – celebratory copy for correct submissions.
- `error_message TEXT` – guidance when the learner submits an incorrect answer.
- `options JSONB NOT NULL` – array of objects containing `id`, `label`,
  optional `description`, and `tally` fields.
- `correct_option_id TEXT NOT NULL` – answer identifier flagged as correct.
- `published_on DATE NOT NULL` – first UTC date the question should be served.
- `expires_on DATE` – exclusive UTC date after which the prompt is retired.
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` – insertion timestamp.
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` – last modification timestamp.

The table carries a descending index on `(published_on, id)` to accelerate
lookups for the current day.

```sql
CREATE INDEX IF NOT EXISTS quiz_questions_active_idx
ON quiz_questions (published_on DESC, id DESC);
```

## Retrieval workflow

`QuizResultsStore.fetch_question_of_day` calculates the caller's UTC date and
runs the following lookup:

```sql
SELECT ...
FROM quiz_questions
WHERE published_on <= %s
  AND (expires_on IS NULL OR expires_on > %s)
ORDER BY published_on DESC, id DESC
LIMIT 1;
```

If a row matches, the backend normalizes option payloads into a list of
dictionaries and returns the values expected by `flashoffer-react`. When no row
qualifies, the handler emits `404 question_not_available`.

## Authoring guidance

- Populate every option with an `id` so analytics and frontend state remain
  stable across releases.
- Set `published_on` to the intended availability date in UTC; omit
  `expires_on` to keep the prompt active until a newer entry is provisioned.
- Store localized tallies inside the `options` JSON object when historic vote
  counts should be displayed alongside each choice.
