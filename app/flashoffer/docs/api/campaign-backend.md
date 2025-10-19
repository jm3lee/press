# Campaign Backend API Guide

The campaign backend provides canonical timelines for every Flashoffer launch.
It powers client countdown timers and internal dashboards that track remaining
inventory. The production base URL is typically
`https://campaign.flashoffer.example`. Authenticate calls with the shared
service token in the `Authorization: Bearer` header.

## Health Check

Use the health probe to confirm that the service and database are reachable.

```bash
curl -i \
  -H "Authorization: Bearer $CAMPAIGN_TOKEN" \
  https://campaign.flashoffer.example/health
```

A `200 OK` response signals that the application can serve traffic. Non-2xx
responses warrant escalation because expiring campaigns will not emit updated
end times.

## Fetching Configuration

Retrieve the deployment configuration to compare environment settings.

```bash
curl -s \
  -H "Authorization: Bearer $CAMPAIGN_TOKEN" \
  https://campaign.flashoffer.example/config |
  jq
```

The response includes the database host, port, and pool sizing details. No
secret values are exposed.

## Retrieving Campaign End Times

The `/api/campaign/<campaign_id>/end_time` endpoint powers real-time countdown
widgets. The route returns both the scheduled close timestamp and the remaining
milliseconds.

```bash
curl -s \
  -H "Authorization: Bearer $CAMPAIGN_TOKEN" \
  https://campaign.flashoffer.example/api/campaign/spring-sprint/end_time |
  jq
```

A typical response contains the following payload:

```json
{
  "campaign_id": "spring-sprint",
  "end_time_utc": "2024-05-10T23:59:59Z",
  "remaining_ms": 86400000
}
```

### Integrating with React Countdown Widgets

Flashoffer React applications can hydrate countdown banners with a simple fetch
helper.

```ts
import { useEffect, useState } from "react";

export function useCampaignDeadline(campaignId: string) {
  const [deadline, setDeadline] = useState<Date | null>(null);

  useEffect(() => {
    async function loadDeadline() {
      const response = await fetch(
        `https://campaign.flashoffer.example/api/campaign/${campaignId}/end_time`,
        {
          headers: {
            Authorization: `Bearer ${process.env.CAMPAIGN_TOKEN}`
          }
        }
      );
      if (!response.ok) {
        throw new Error(`Failed to load campaign deadline: ${response.status}`);
      }
      const body = await response.json();
      setDeadline(new Date(body.end_time_utc));
    }

    void loadDeadline();
  }, [campaignId]);

  return deadline;
}
```

This hook converts the UTC string into a `Date` instance for countdown math. A
polling wrapper can re-query the endpoint every minute to keep timers precise.
