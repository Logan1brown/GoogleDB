-- Migration: Create Support Tables
-- Created: 2025-04-08

-- Rollback if needed
DROP TABLE IF EXISTS networks CASCADE;
DROP TABLE IF EXISTS studios CASCADE;
DROP TABLE IF EXISTS genres CASCADE;
DROP TABLE IF EXISTS subgenres CASCADE;
DROP TABLE IF EXISTS status_types CASCADE;
DROP TABLE IF EXISTS order_types CASCADE;
DROP TABLE IF EXISTS source_types CASCADE;
DROP FUNCTION IF EXISTS update_updated_at();

-- Enable Row Level Security
ALTER DATABASE postgres SET "auth.enabled" = true;

-- Create Networks Table
CREATE TABLE networks (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    search_name TEXT GENERATED ALWAYS AS (LOWER(name)) STORED,
    type TEXT NOT NULL,  -- Using TEXT as we have various types like 'Broadcast', 'Cable', etc.
    parent_company TEXT,
    aliases TEXT[],
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT networks_name_unique UNIQUE (name),
    CONSTRAINT networks_search_name_unique UNIQUE (search_name)
);

-- Create indexes for networks
CREATE INDEX idx_networks_name ON networks(name);
CREATE INDEX idx_networks_search_name ON networks(search_name);
CREATE INDEX idx_networks_type ON networks(type);
CREATE INDEX idx_networks_parent_company ON networks(parent_company);

-- Create Studios Table
CREATE TABLE studios (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    search_name TEXT GENERATED ALWAYS AS (LOWER(name)) STORED,
    type TEXT,  -- e.g., 'Studio'
    parent_company TEXT,
    division TEXT,  -- e.g., 'Disney Television Studios'
    platform TEXT,  -- e.g., 'Disney+'
    category TEXT[], -- Can have multiple like 'Vertically Integrated', 'Network-First'
    aliases TEXT[],
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT studios_name_unique UNIQUE (name),
    CONSTRAINT studios_search_name_unique UNIQUE (search_name)
);

-- Create indexes for studios
CREATE INDEX idx_studios_name ON studios(name);
CREATE INDEX idx_studios_search_name ON studios(search_name);
CREATE INDEX idx_studios_parent_company ON studios(parent_company);
CREATE INDEX idx_studios_platform ON studios(platform);

-- Create Genres Table
CREATE TABLE genres (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    search_name TEXT GENERATED ALWAYS AS (LOWER(name)) STORED,
    category TEXT,  -- e.g., 'Main', 'Sub'
    aliases TEXT[],
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT genres_name_unique UNIQUE (name),
    CONSTRAINT genres_search_name_unique UNIQUE (search_name)
);

-- Create indexes for genres
CREATE INDEX idx_genres_name ON genres(name);
CREATE INDEX idx_genres_search_name ON genres(search_name);
CREATE INDEX idx_genres_category ON genres(category);

-- Create Secondary Genres Table (renamed from subgenres for clarity)
CREATE TABLE subgenres (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    search_name TEXT GENERATED ALWAYS AS (LOWER(name)) STORED,
    category TEXT,  -- e.g., 'Main'
    aliases TEXT[],
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT subgenres_name_unique UNIQUE (name),
    CONSTRAINT subgenres_search_name_unique UNIQUE (search_name)
);

-- Create Order Types Table
CREATE TABLE order_types (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    search_name TEXT GENERATED ALWAYS AS (LOWER(name)) STORED,
    description TEXT,  -- e.g., 'One-season only, planned ending'
    aliases TEXT[],  -- e.g., ['Limited Series', 'Mini-Series', 'Event Series']
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create Role Types Table
CREATE TABLE role_types (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,  -- e.g., 'Creator'
    category TEXT,  -- e.g., 'Creative'
    aliases TEXT[],  -- e.g., ['c', 'Created By', 'Creator/EP']
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create Source Types Table
CREATE TABLE source_types (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,  -- e.g., 'Original'
    category TEXT,  -- e.g., 'Original'
    aliases TEXT[],  -- e.g., ['New IP', 'Original Content']
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create Status Types Table
CREATE TABLE status_types (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,  -- e.g., 'Active'
    description TEXT,  -- e.g., 'Currently airing or in production'
    aliases TEXT[],  -- e.g., ['Running', 'Current', 'In Production']
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_networks_name ON networks(name);
CREATE INDEX idx_networks_type ON networks(type);
CREATE INDEX idx_studios_name ON studios(name);
CREATE INDEX idx_genres_name ON genres(name);
CREATE INDEX idx_subgenres_name ON subgenres(name);
CREATE INDEX idx_order_types_name ON order_types(name);
CREATE INDEX idx_role_types_name ON role_types(name);
CREATE INDEX idx_source_types_name ON source_types(name);
CREATE INDEX idx_status_types_name ON status_types(name);

-- Add updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
CREATE TRIGGER update_networks_updated_at
    BEFORE UPDATE ON networks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_studios_updated_at
    BEFORE UPDATE ON studios
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_genres_updated_at
    BEFORE UPDATE ON genres
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_subgenres_updated_at
    BEFORE UPDATE ON subgenres
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_order_types_updated_at
    BEFORE UPDATE ON order_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_role_types_updated_at
    BEFORE UPDATE ON role_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_source_types_updated_at
    BEFORE UPDATE ON source_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_status_types_updated_at
    BEFORE UPDATE ON status_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security (RLS)
ALTER TABLE networks ENABLE ROW LEVEL SECURITY;
ALTER TABLE studios ENABLE ROW LEVEL SECURITY;
ALTER TABLE genres ENABLE ROW LEVEL SECURITY;
ALTER TABLE subgenres ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE status_types ENABLE ROW LEVEL SECURITY;

-- Comments for documentation
COMMENT ON TABLE networks IS 'TV Networks and Streaming Platforms';
COMMENT ON TABLE studios IS 'Production Studios';
COMMENT ON TABLE genres IS 'Show Genres';
COMMENT ON TABLE subgenres IS 'Secondary genre tags for shows (2nd and 3rd TMDB genre tags)';
COMMENT ON TABLE order_types IS 'Types of show orders (Limited, etc.)';
COMMENT ON TABLE role_types IS 'Creative and production roles';
COMMENT ON TABLE source_types IS 'Show source types (Original, etc.)';
COMMENT ON TABLE status_types IS 'Show status types (Active, etc.)';
