-- Migration: Create Main Tables
-- Created: 2025-04-08

-- Rollback if needed
DROP MATERIALIZED VIEW IF EXISTS show_team_stats;
DROP MATERIALIZED VIEW IF EXISTS show_details;
DROP TABLE IF EXISTS show_team CASCADE;
DROP TABLE IF EXISTS shows CASCADE;

-- Create Shows Table
CREATE TABLE shows (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,  -- Standardized from: shows.shows, show_team.show_name, TMDB_success_metrics.Title
    search_title TEXT GENERATED ALWAYS AS (LOWER(title)) STORED,  -- For case-insensitive search
    description TEXT,
    status_id BIGINT REFERENCES status_types(id),
    network_id BIGINT REFERENCES networks(id),
    studio_id BIGINT REFERENCES studios(id),  -- Primary studio (first one listed)
    genre_id BIGINT REFERENCES genres(id),  -- Primary genre
    subgenres BIGINT[],  -- Additional genres
    source_type_id BIGINT REFERENCES source_types(id),
    order_type_id BIGINT REFERENCES order_types(id),
    date DATE,  -- Original date from source
    episode_count INTEGER,  -- Number of episodes
    tmdb_id INTEGER UNIQUE,  -- TMDB ID for external reference
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT shows_title_unique UNIQUE (title),
    CONSTRAINT shows_search_title_unique UNIQUE (search_title)
);

-- Create Team Members Table
CREATE TABLE show_team (
    id BIGSERIAL PRIMARY KEY,
    show_id BIGINT NOT NULL REFERENCES shows(id),  -- Show reference
    name TEXT NOT NULL,  -- Name as credited
    search_name TEXT GENERATED ALWAYS AS (LOWER(name)) STORED,  -- For search
    role_type_id BIGINT NOT NULL REFERENCES role_types(id),  -- Normalized role
    team_order INTEGER,  -- For display priority
    notes TEXT,  -- Additional information
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT show_team_unique UNIQUE (show_id, name, role_type_id)
);

-- Add indexes for frequent queries

-- Shows table indexes
CREATE INDEX idx_shows_title ON shows(title);  -- Exact matches
CREATE INDEX idx_shows_search_title ON shows(search_title);  -- Case-insensitive search
CREATE INDEX idx_shows_network_id ON shows(network_id);  -- Network lookups
CREATE INDEX idx_shows_studio_id ON shows(studio_id);  -- Studio lookups
CREATE INDEX idx_shows_genre_id ON shows(genre_id);  -- Genre lookups
CREATE INDEX idx_shows_status_id ON shows(status_id);  -- Status lookups

-- Show team table indexes
CREATE INDEX idx_show_team_show_id ON show_team(show_id);  -- Show lookups
CREATE INDEX idx_show_team_name ON show_team(name);  -- Exact matches
CREATE INDEX idx_show_team_search_name ON show_team(search_name);  -- Name search
CREATE INDEX idx_show_team_role_type_id ON show_team(role_type_id);  -- Role lookups

-- Add array index for subgenres to improve array operations
CREATE INDEX idx_shows_subgenres ON shows USING GIN(subgenres);


-- Add triggers for updated_at
CREATE TRIGGER update_shows_updated_at
    BEFORE UPDATE ON shows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_show_team_updated_at
    BEFORE UPDATE ON show_team
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE shows ENABLE ROW LEVEL SECURITY;
ALTER TABLE show_team ENABLE ROW LEVEL SECURITY;

-- Comments for documentation
COMMENT ON TABLE shows IS 'TV Shows and Series - Standardized from multiple source sheets';
COMMENT ON COLUMN shows.title IS 'Show title, standardized from: shows.shows, show_team.show_name, TMDB_success_metrics.Title';
COMMENT ON TABLE show_team IS 'Creative team members associated with shows, with normalized roles';

-- Create materialized views for common queries
-- Create materialized view for show details with search fields
CREATE MATERIALIZED VIEW show_details AS
SELECT 
    s.*,
    n.name as network_name,
    n.search_name as network_search,
    st.name as studio_name,
    st.search_name as studio_search,
    g.name as genre_name,
    g.search_name as genre_search
FROM shows s
LEFT JOIN networks n ON s.network_id = n.id
LEFT JOIN studios st ON s.studio_id = st.id
LEFT JOIN genres g ON s.genre_id = g.id;

CREATE UNIQUE INDEX idx_show_details_id ON show_details (id);
CREATE INDEX idx_show_details_search ON show_details (search_title);

-- Create materialized view for team member stats
CREATE MATERIALIZED VIEW show_team_stats AS
SELECT
    s.title as show_title,
    COUNT(*) as total_members,
    COUNT(DISTINCT st.roles) as unique_roles,
    array_agg(DISTINCT st.roles) as role_types,
    MAX(st.created_at) as last_updated
FROM show_team st
JOIN shows s ON st.show_id = s.id

WHERE st.active = true
GROUP BY s.title;

CREATE UNIQUE INDEX idx_show_team_stats_member ON show_team_stats (show_title);
