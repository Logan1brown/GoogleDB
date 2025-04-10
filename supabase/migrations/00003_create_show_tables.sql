-- Migration: Create Show Tables
-- Created: 2025-04-09

-- Create shows table
CREATE TABLE shows (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    search_title TEXT GENERATED ALWAYS AS (LOWER(title)) STORED,
    description TEXT,
    network_id BIGINT REFERENCES network_list(id),
    genre_id BIGINT REFERENCES genre_list(id),
    subgenres BIGINT[] DEFAULT '{}',
    studios BIGINT[] DEFAULT '{}',  -- Array of studio IDs, both regular studios and production companies
    status_id BIGINT REFERENCES status_types(id),
    source_type_id BIGINT REFERENCES source_types(id),
    order_type_id BIGINT REFERENCES order_types(id),
    date DATE,
    episode_count INTEGER,
    tmdb_id INTEGER UNIQUE,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT shows_title_unique UNIQUE (title),
    CONSTRAINT shows_search_title_unique UNIQUE (search_title)
);

-- Create show_team table
CREATE TABLE show_team (
    id BIGSERIAL PRIMARY KEY,
    show_id BIGINT NOT NULL REFERENCES shows(id),
    name TEXT NOT NULL,
    search_name TEXT GENERATED ALWAYS AS (LOWER(name)) STORED,
    role_type_id BIGINT NOT NULL REFERENCES role_types(id),
    team_order INTEGER,
    notes TEXT,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT show_team_unique UNIQUE (show_id, name, role_type_id)
);

-- Create tmdb_metrics table
CREATE TABLE tmdb_metrics (
    id BIGSERIAL PRIMARY KEY,
    tmdb_id INTEGER NOT NULL REFERENCES shows(tmdb_id),
    seasons INTEGER,
    episodes_per_season INTEGER[],
    total_episodes INTEGER,
    average_episodes FLOAT,
    status TEXT,
    last_air_date DATE,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT tmdb_metrics_tmdb_id_unique UNIQUE (tmdb_id)
);

-- Add indexes
CREATE INDEX idx_shows_title ON shows(title);
CREATE INDEX idx_shows_search_title ON shows(search_title);
CREATE INDEX idx_shows_network_id ON shows(network_id);
CREATE INDEX idx_shows_genre_id ON shows(genre_id);
CREATE INDEX idx_shows_status_id ON shows(status_id);
CREATE INDEX idx_shows_source_type_id ON shows(source_type_id);
CREATE INDEX idx_shows_order_type_id ON shows(order_type_id);
CREATE INDEX idx_shows_tmdb_id ON shows(tmdb_id) WHERE tmdb_id IS NOT NULL;
CREATE INDEX idx_shows_subgenres ON shows USING GIN(subgenres);
CREATE INDEX idx_shows_studios ON shows USING GIN(studios);

CREATE INDEX idx_show_team_show_id ON show_team(show_id);
CREATE INDEX idx_show_team_name ON show_team(name);
CREATE INDEX idx_show_team_search_name ON show_team(search_name);
CREATE INDEX idx_show_team_role_type_id ON show_team(role_type_id);

CREATE INDEX idx_tmdb_metrics_tmdb_id ON tmdb_metrics(tmdb_id);

-- Add triggers for updated_at
CREATE TRIGGER update_shows_updated_at
    BEFORE UPDATE ON shows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_show_team_updated_at
    BEFORE UPDATE ON show_team
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_tmdb_metrics_updated_at
    BEFORE UPDATE ON tmdb_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE shows ENABLE ROW LEVEL SECURITY;
ALTER TABLE show_team ENABLE ROW LEVEL SECURITY;
ALTER TABLE tmdb_metrics ENABLE ROW LEVEL SECURITY;

-- Add comments
COMMENT ON TABLE shows IS 'TV Shows and Series - Standardized from multiple source sheets';
COMMENT ON COLUMN shows.title IS 'Show title, standardized from: shows.shows, show_team.show_name, TMDB_success_metrics.Title';
COMMENT ON COLUMN shows.studios IS 'Array of studio IDs, including both regular studios and production companies';
COMMENT ON TABLE show_team IS 'Creative team members associated with shows, with normalized roles';
COMMENT ON TABLE tmdb_metrics IS 'TMDB-specific metrics and episode data';
