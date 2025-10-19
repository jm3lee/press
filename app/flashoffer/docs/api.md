# Flashoffer API Directory

This document provides a high-level map of the public routes exposed by the
Flashoffer backends. Each service is deployed independently and fronts its own
base URL, but the path and behaviour summaries below are stable across
environments.

## Analytics Backend

| Path | Methods | Summary |
| --- | --- | --- |
| `/health` | `GET` | Liveness probe that confirms database reachability. |
| `/events` | `OPTIONS` | CORS preflight for the events ingestion endpoint. |
| `/events` | `POST` | Accepts batched analytics events for a session and persists them. |
| `/events/recent` | `OPTIONS` | CORS preflight for the recent events listing. |
| `/events/recent` | `GET` | Returns the most recent events, capped to 200 records. |
| `/config` | `GET` | Emits a redacted configuration snapshot (database host and port). |

## Campaign Backend

| Path | Methods | Summary |
| --- | --- | --- |
| `/health` | `GET` | Liveness probe that verifies database connectivity. |
| `/config` | `GET` | Returns the effective database connection coordinates. |
| `/api/campaign/<campaign_id>/end_time` | `OPTIONS` | CORS preflight for campaign deadline lookups. |
| `/api/campaign/<campaign_id>/end_time` | `GET` | Fetches the campaign end timestamp and remaining milliseconds. |

## Quiz Backend

| Path | Methods | Summary |
| --- | --- | --- |
| `/health` | `GET` | Liveness probe that ensures the quiz database is reachable. |
| `/api/quiz/events` | `OPTIONS` | CORS preflight for quiz event ingestion and listing. |
| `/api/quiz/events` | `POST` | Records quiz completion events and aggregates attempts/passes. |
| `/api/quiz/events` | `GET` | Lists recent quiz completion events with optional campaign filter. |
| `/api/quiz/today` | `OPTIONS` | CORS preflight for the question-of-the-day endpoint. |
| `/api/quiz/today` | `GET` | Returns the active question of the day when one is published. |
| `/api/quiz/questions` | `OPTIONS` | CORS preflight for listing and creation of quiz questions. |
| `/api/quiz/questions` | `GET` | Paginates through stored quiz questions. |
| `/api/quiz/questions` | `POST` | Validates and stores a new quiz question payload. |
| `/api/quiz/questions/<slug>` | `OPTIONS` | CORS preflight for quiz question updates. |
| `/api/quiz/questions/<slug>` | `PUT` | Updates an existing quiz question identified by slug. |
| `/api/quiz/questions/generate` | `OPTIONS` | CORS preflight for AI-assisted question generation. |
| `/api/quiz/questions/generate` | `POST` | Calls the OpenAI API to draft a question and returns the raw payload. |
| `/config` | `GET` | Emits a trimmed configuration snapshot (database host and port). |
