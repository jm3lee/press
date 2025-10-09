-- provision storage for engagement events
CREATE TABLE IF NOT EXISTS engagement_events (
    id BIGSERIAL NOT NULL,
    site TEXT NOT NULL,
    session_id UUID NOT NULL,
    event_type TEXT NOT NULL,
    target TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    meta JSONB NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (occurred_at, id)
)
