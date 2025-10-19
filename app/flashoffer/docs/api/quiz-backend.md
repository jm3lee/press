# Quiz Backend API Guide

The quiz backend manages the interactive assessments that gate Flashoffer
campaigns. It stores questions, evaluates completions, and publishes the daily
quiz. Production deployments live at `https://quiz.flashoffer.example` and
require the shared bearer token for access.

## Health Check

Monitor uptime via the health probe.

```bash
curl -i \
  -H "Authorization: Bearer $QUIZ_TOKEN" \
  https://quiz.flashoffer.example/health
```

## Working with Quiz Events

The `/api/quiz/events` collection lets you submit completion events and review
recent attempts. Payloads include the user identifier, campaign context, and the
score awarded by the grading flow.

```bash
curl -i \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $QUIZ_TOKEN" \
  https://quiz.flashoffer.example/api/quiz/events \
  -d '{
    "campaign_id": "spring-sprint",
    "user_id": "user-8421",
    "score": 4,
    "max_score": 5,
    "passed": true
  }'
```

The service responds with `201 Created` and echoes the stored record. Query the
same collection with `GET` to list the most recent 200 events.

```bash
curl -s \
  -H "Authorization: Bearer $QUIZ_TOKEN" \
  "https://quiz.flashoffer.example/api/quiz/events?campaign_id=spring-sprint" |
  jq '.[0:5]'
```

Each entry contains the original payload plus a `recorded_at` timestamp for
analytics pipelines.

## Publishing the Question of the Day

When a campaign uses the daily quiz mechanic, content managers publish the
question via `/api/quiz/today`. The `GET` route returns metadata about the
current question, including the prompt, choices, and the scheduled expiration.

```bash
curl -s \
  -H "Authorization: Bearer $QUIZ_TOKEN" \
  https://quiz.flashoffer.example/api/quiz/today |
  jq
```

Use the response to hydrate marketing surfaces or send reminder notifications.
If no question is active the service returns `404 Not Found`.

## Managing the Question Bank

Authoring flows rely on the `/api/quiz/questions` collection. Use the `POST`
route to insert new questions with validation.

```bash
curl -i \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $QUIZ_TOKEN" \
  https://quiz.flashoffer.example/api/quiz/questions \
  -d '{
    "prompt": "How long does the Flashoffer boost stay active?",
    "choices": [
      "24 hours",
      "48 hours",
      "72 hours",
      "Until the campaign ends"
    ],
    "answer_index": 3,
    "campaign_ids": ["spring-sprint"],
    "difficulty": "medium"
  }'
```

The service enforces choice uniqueness and answer index bounds. Update an
existing question by targeting its slug.

```bash
curl -i \
  -X PUT \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $QUIZ_TOKEN" \
  https://quiz.flashoffer.example/api/quiz/questions/how-long-does-the-boost-last \
  -d '{
    "answer_index": 2,
    "difficulty": "hard"
  }'
```

A successful update returns the revised question object. To bootstrap content,
call the AI-assisted generator.

```bash
curl -s \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $QUIZ_TOKEN" \
  https://quiz.flashoffer.example/api/quiz/questions/generate \
  -d '{"topic": "cashback basics", "difficulty": "easy"}' |
  jq
```

The generator responds with a draft question and choices that your moderation
workflow can review before publishing.
