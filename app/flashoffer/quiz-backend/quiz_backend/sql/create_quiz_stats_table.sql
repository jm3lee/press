-- maintain aggregate counts of quiz answer outcomes
CREATE TABLE IF NOT EXISTS quiz_question_stats (
    quiz_id TEXT PRIMARY KEY,
    correct_answers BIGINT NOT NULL DEFAULT 0,
    incorrect_answers BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
