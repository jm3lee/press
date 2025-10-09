-- persist a quiz completion record
INSERT INTO quiz_results (
    quiz_id,
    user_id,
    attempt_id,
    occurred_at,
    attempts,
    passes,
    fails,
    payload
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id, received_at
