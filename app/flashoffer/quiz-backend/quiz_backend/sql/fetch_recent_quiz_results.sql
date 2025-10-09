-- retrieve recent quiz completion results optionally filtered by campaign
SELECT
    id,
    quiz_id,
    user_id,
    attempt_id,
    campaign_id,
    occurred_at,
    attempts,
    passes,
    fails,
    payload,
    received_at
FROM quiz_results
WHERE (%s IS NULL OR campaign_id = %s)
ORDER BY received_at DESC
LIMIT %s
