-- maintain supporting index for daily question lookups
CREATE INDEX IF NOT EXISTS quiz_questions_active_idx
ON quiz_questions (published_on DESC, id DESC);
