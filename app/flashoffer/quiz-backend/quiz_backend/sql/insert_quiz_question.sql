-- insert a new quiz question and return the stored record
INSERT INTO quiz_questions (
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
) VALUES (
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s
)
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
    created_at,
    updated_at;
