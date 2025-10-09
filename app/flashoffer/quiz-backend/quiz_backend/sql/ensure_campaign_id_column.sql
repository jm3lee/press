-- guarantee the optional campaign reference exists
ALTER TABLE quiz_results
ADD COLUMN IF NOT EXISTS campaign_id TEXT;
