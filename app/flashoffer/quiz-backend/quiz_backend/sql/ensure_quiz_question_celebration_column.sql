-- add optional celebration configuration for quiz questions
ALTER TABLE quiz_questions
ADD COLUMN IF NOT EXISTS celebration TEXT NOT NULL DEFAULT 'off';
