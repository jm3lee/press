-- fetch quiz questions ordered by most recent publish date
SELECT
    id,
    slug,
    question,
    helper_text,
    explanation,
    success_message,
    error_message,
    options,
    correct_option_id,
    published_on,
    expires_on,
    created_at,
    updated_at
FROM quiz_questions
ORDER BY published_on DESC, id DESC
LIMIT %s
OFFSET %s;
