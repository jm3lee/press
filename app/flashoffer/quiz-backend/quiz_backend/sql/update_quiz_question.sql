-- update an existing quiz question identified by slug
UPDATE quiz_questions
SET
    question = %s,
    helper_text = %s,
    explanation = %s,
    success_message = %s,
    error_message = %s,
    options = %s,
    correct_option_id = %s,
    published_on = %s,
    expires_on = %s,
    celebration = %s,
    updated_at = NOW()
WHERE slug = %s
RETURNING
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
    celebration,
    created_at,
    updated_at;
