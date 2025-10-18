-- retrieve the active quiz question for the provided date
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
    expires_on
FROM quiz_questions
WHERE published_on <= %s
  AND (expires_on IS NULL OR expires_on > %s)
ORDER BY published_on DESC, id DESC
LIMIT 1
