-- Migration: Update Shows Schema
-- Created: 2025-04-08

-- Update shows table
ALTER TABLE shows
    -- Remove TMDB metrics
    DROP COLUMN IF EXISTS tmdb_popularity,
    DROP COLUMN IF EXISTS tmdb_vote_average,
    DROP COLUMN IF EXISTS tmdb_vote_count,
    
    -- Add new columns
    ADD COLUMN IF NOT EXISTS date DATE,
    ADD COLUMN IF NOT EXISTS episode_count INTEGER,
    
    -- Rename subgenre_ids to subgenres if it exists
    ALTER COLUMN subgenre_ids SET DATA TYPE BIGINT[] USING subgenre_ids::BIGINT[],
    ALTER COLUMN subgenre_ids SET DEFAULT '{}',
    RENAME COLUMN subgenre_ids TO subgenres;

-- Update show_team table
ALTER TABLE show_team
    -- Drop old roles column if it exists
    DROP COLUMN IF EXISTS roles,
    
    -- Add role_type_id if not exists
    ADD COLUMN IF NOT EXISTS role_type_id BIGINT REFERENCES role_types(id),
    
    -- Drop old unique constraint
    DROP CONSTRAINT IF EXISTS show_team_show_id_name_key,
    
    -- Add new composite unique constraint
    ADD CONSTRAINT show_team_unique UNIQUE (show_id, name, role_type_id);

-- Add comments documenting the standardization
COMMENT ON TABLE shows IS 'TV Shows and Series - Standardized from multiple source sheets';
COMMENT ON COLUMN shows.title IS 'Show title, standardized from: shows.shows, show_team.show_name, TMDB_success_metrics.Title';
COMMENT ON TABLE show_team IS 'Creative team members associated with shows, with normalized roles';

-- Update materialized views
REFRESH MATERIALIZED VIEW show_details;
