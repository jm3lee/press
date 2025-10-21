-- retrieve aggregate stats for a quiz id
SELECT
    quiz_id,
    correct_answers,
    incorrect_answers,
    created_at,
    updated_at
FROM quiz_question_stats
WHERE quiz_id = %s
