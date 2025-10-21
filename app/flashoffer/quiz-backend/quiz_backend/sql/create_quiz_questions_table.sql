-- ensure quiz question catalog exists
CREATE TABLE IF NOT EXISTS quiz_questions (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    question TEXT NOT NULL,
    helper_text TEXT,
    explanation TEXT,
    success_message TEXT,
    error_message TEXT,
    options JSONB NOT NULL,
    correct_option_id TEXT NOT NULL,
    published_on DATE NOT NULL,
    expires_on DATE,
    celebration TEXT NOT NULL DEFAULT 'off',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
