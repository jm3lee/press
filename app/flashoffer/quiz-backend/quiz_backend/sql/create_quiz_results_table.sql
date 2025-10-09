-- ensure quiz results storage exists
CREATE TABLE IF NOT EXISTS quiz_results (
    id BIGSERIAL PRIMARY KEY,
    quiz_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    attempt_id TEXT,
    campaign_id TEXT,
    occurred_at TIMESTAMPTZ NOT NULL,
    attempts INTEGER NOT NULL,
    passes INTEGER NOT NULL,
    fails INTEGER NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
