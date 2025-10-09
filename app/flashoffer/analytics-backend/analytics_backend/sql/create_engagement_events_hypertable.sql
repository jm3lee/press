-- convert engagement_events into a hypertable
SELECT create_hypertable('engagement_events', 'occurred_at', if_not_exists => TRUE)
