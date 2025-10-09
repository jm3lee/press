-- fetch the most recently received engagement events
SELECT
    id,
    site,
    session_id,
    event_type,
    target,
    occurred_at,
    meta,
    received_at
FROM engagement_events
ORDER BY received_at DESC
LIMIT %s
