-- Create TMDB success metrics table
CREATE TABLE IF NOT EXISTS tmdb_success_metrics (
    id BIGSERIAL PRIMARY KEY,
    tmdb_id INTEGER REFERENCES shows(tmdb_id),
    seasons INTEGER,
    episodes_per_season INTEGER[],
    total_episodes INTEGER,
    average_episodes FLOAT,
    status TEXT,
    last_air_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add indexes
CREATE INDEX IF NOT EXISTS tmdb_success_metrics_tmdb_id_idx ON tmdb_success_metrics(tmdb_id);
CREATE INDEX IF NOT EXISTS tmdb_success_metrics_status_idx ON tmdb_success_metrics(status);

-- Add trigger for updated_at
CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON tmdb_success_metrics
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_set_timestamp();
