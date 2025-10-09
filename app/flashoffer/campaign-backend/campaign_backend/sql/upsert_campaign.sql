-- upsert the campaign deadline metadata
INSERT INTO campaign (id, end_time)
VALUES (%s, %s)
ON CONFLICT (id)
DO UPDATE SET end_time = EXCLUDED.end_time,
    updated_at = NOW()
