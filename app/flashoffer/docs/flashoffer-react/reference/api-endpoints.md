# Flashoffer React API endpoints

Flashoffer React coordinates with several backend endpoints to retrieve campaign
metadata and capture engagement analytics. This guide summarizes the network
contracts that the library expects so backend and frontend teams can integrate
reliably.

## Campaign countdown endpoint

`CountdownTimer` resolves campaign end times by issuing a `GET` request to
`/api/campaign/<campaign-id>/end_time`. The component accepts `campaignId` as a
prop; the value is URL encoded before the request is dispatched.

The handler should return JSON encoded data and respond with a `2xx` status when
the lookup succeeds. `CountdownTimer` understands multiple field names to ease
integration with existing services:

- `remainingMs`, `remaining_ms`, or `remainingMilliseconds` describe the number
  of milliseconds until the campaign expires.
- `endTime`, `end_time`, or `deadline` provide the campaign end timestamp as an
  ISO-8601 string, JavaScript timestamp, or `Date` serialized value.

When both sets appear in the same payload, the timer prefers the remaining
millisecond counters. The component expects the server to emit cacheable
responses and will re-fetch only when its `campaignId` prop changes.

## Engagement ingestion endpoint

`EngagementProvider` batches view, scroll, and interaction events before
flushing them to the configured `endpoint` via `POST` requests. The provider
includes credentials to support cookie-bound sessions and falls back to
`navigator.sendBeacon` when synchronous delivery is requested (for example,
during page unload).

Each payload follows this schema:

```json
{
  "site": "flashoffer-demo",
  "session_id": "2a354d9d-c0d0-4b4f-a274-030a5ec6a1ad",
  "campaign_id": "spring-promo",
  "reason": "interval",
  "events": [
    {
      "type": "view",
      "target": "hero",
      "meta": { "ratio": 0.82 },
      "at": "2024-04-08T16:02:31.514Z"
    }
  ]
}
```

The `campaign_id` field is omitted when no campaign identifier is provided to
`EngagementProvider`. Servers should respond with `204` (or `200`) to confirm
receipt; any non-success status causes the provider to retry up to ten times
before permanently disabling collection for the session.

## Event stream endpoint

Components that visualize historic activity, such as `EventConsole`, poll a
read-only endpoint to fetch captured engagement events. Configure the
`eventsUrl` prop with the endpoint path. The hook `useEventStream` issues `GET`
requests that include the caller-specified `limit` parameter unless the query
already sets it. Pass the optional `authToken` to send a
`Bearer <token>` authorization header.

The endpoint should respond with JSON matching the shape returned by the
Flashoffer engagement backend:

```json
{
  "events": [
    {
      "id": "evt-42",
      "event_type": "cta_click",
      "target": "hero",
      "occurred_at": "2024-04-08T16:02:31.514Z",
      "received_at": "2024-04-08T16:02:32.019Z",
      "site": "flashoffer-demo",
      "session_id": "2a354d9d-c0d0-4b4f-a274-030a5ec6a1ad",
      "meta": { "cta": "Sign up" }
    }
  ]
}
```

When the endpoint cannot service the request, it should reply with an explicit
HTTP status code and descriptive message. The hook transitions to an error state
and stops polling when it receives a network error or a non-success response.

## Quiz analytics endpoint

`logQuizCompletion` posts quiz results to the Flashoffer quiz analytics service.
Callers supply the endpoint through `QuizAnalyticsOptions`. The helper issues a
`POST` request with `Content-Type: application/json`, includes credentials for
cookie-bound sessions, and marks the request as `keepalive` so browsers deliver
it even when navigating away.

The payload contains normalized quiz metadata:

```json
{
  "quiz_id": "weekly-trivia",
  "user_id": "current-session-id",
  "event_type": "complete",
  "passed": true,
  "campaign_id": "spring-promo",
  "metadata": {
    "question": "How many offers run per week?",
    "selected_option_id": "opt-b",
    "correct_option_id": "opt-b",
    "attempt": 1
  },
  "occurred_at": "2024-04-08T16:02:31.514Z"
}
```

Servers should treat unspecified `campaign_id` fields as optional and may ignore
`metadata.correct_option_id` when the quiz does not reveal answers. Respond with
`2xx` to acknowledge the event; otherwise the helper logs a warning and the
caller can retry manually if needed.

## End-to-end integration example

The snippet below wires the primary endpoints together. It loads the campaign
countdown, records engagement, streams recent events, and logs quiz results.

```tsx
import { useCallback } from "react";
import {
  CountdownTimer,
  EngagementProvider,
  EventConsole,
  MultipleChoiceQuiz,
  logQuizCompletion,
} from "@flashoffer/react";

const quizEndpoint = "/api/quiz/events";
const engagementEndpoint = "/api/engagement/events";
const eventStreamUrl = "/api/engagement/events/recent";

export function CampaignExperience() {
  const handleQuizSubmit = useCallback(async (payload) => {
    await logQuizCompletion(payload, {
      quizId: payload.questionId,
      endpoint: quizEndpoint,
    });
  }, []);

  return (
    <EngagementProvider site="flashoffer-demo" endpoint={engagementEndpoint}>
      <CountdownTimer campaignId="spring-promo" />
      <MultipleChoiceQuiz onSubmit={handleQuizSubmit} />
      <EventConsole eventsUrl={eventStreamUrl} />
    </EngagementProvider>
  );
}
```

This pattern keeps the frontend aligned with the expectations encoded in the
Flashoffer React components and minimizes surprises when backend implementations
change.
