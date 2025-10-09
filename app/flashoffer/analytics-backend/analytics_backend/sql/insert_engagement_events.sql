-- bulk insert engagement events
INSERT INTO engagement_events (
    site,
    session_id,
    event_type,
    target,
    occurred_at,
    meta
) VALUES %s
