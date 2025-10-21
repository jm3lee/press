-- increment aggregate quiz stats for a specific quiz id
INSERT INTO quiz_question_stats (
    quiz_id,
    correct_answers,
    incorrect_answers
) VALUES (%s, %s, %s)
ON CONFLICT (quiz_id) DO UPDATE SET
    correct_answers = quiz_question_stats.correct_answers + EXCLUDED.correct_answers,
    incorrect_answers = quiz_question_stats.incorrect_answers + EXCLUDED.incorrect_answers,
    updated_at = NOW()
RETURNING quiz_id, correct_answers, incorrect_answers, created_at, updated_at
