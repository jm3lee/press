# Analytics Backend API Guide

The analytics service records client-side interaction telemetry and exposes
recent activity for dashboards. All routes are served from the analytics base
URL, typically `https://analytics.flashoffer.example` in production. Requests
must include a service token in the `Authorization: Bearer` header. Provide the
token value as `<token>` in the header field.

## Health Check

Use the health probe for uptime monitoring.

```bash
curl -i \
  -H "Authorization: Bearer $ANALYTICS_TOKEN" \
  https://analytics.flashoffer.example/health
```

A `200 OK` response confirms that the application and database connection are
healthy. Any non-2xx response should trigger an alert because the ingestion
pipeline will no longer accept events.

## Recording Events

Submit batched analytics payloads with the `/events` endpoint. Each payload
contains the session metadata and an array of events collected on the client.

```bash
curl -i \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ANALYTICS_TOKEN" \
  https://analytics.flashoffer.example/events \
  -d '{
    "session_id": "ca7af53d-b017-4f9e-9838-cc0d11dcb5b8",
    "campaign_id": "spring-sprint",
    "events": [
      {"type": "view", "screen": "offer", "ts_ms": 1712751122334},
      {"type": "cta_click", "cta": "Apply now", "ts_ms": 1712751124123}
    ]
  }'
```

The service validates timestamps and persists each event individually. A
successful call returns `202 Accepted` with an empty body, signalling that the
batch is queued for processing.

### Client-Side Example

Applications using the Flashoffer React SDK can send telemetry with the
following helper:

```ts
import { sendAnalyticsBatch } from "@flashoffer/analytics-client";

await sendAnalyticsBatch({
  sessionId: window.flashoffer.sessionId,
  campaignId: "spring-sprint",
  events: [
    { type: "view", screen: "offer", tsMs: Date.now() },
    { type: "cta_click", cta: "Apply now", tsMs: Date.now() }
  ]
});
```

The SDK handles retries and backoff, so only the payload assembly is required.

## Listing Recent Events

The `/events/recent` route surfaces the latest 200 events for operational
monitoring. Filter the results by campaign with the `campaign_id` query
parameter.

```bash
curl -s \
  -H "Authorization: Bearer $ANALYTICS_TOKEN" \
  "https://analytics.flashoffer.example/events/recent?campaign_id=spring-sprint" |
  jq '.[0:3]'
```

The endpoint returns an array sorted by `ts_ms` descending. Each entry includes
the normalized event fields and the session identifier for traceability.

## Configuration Snapshot

The `/config` route exposes a trimmed view of the deployment settings. Use it
to compare staging and production infrastructure without leaking secrets.

```bash
curl -s \
  -H "Authorization: Bearer $ANALYTICS_TOKEN" \
  https://analytics.flashoffer.example/config |
  jq
```

Expect keys such as `database_host`, `database_port`, and `retention_days`.
