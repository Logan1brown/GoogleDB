-- Migration: Clean up tables
-- Created: 2025-04-08

-- Drop unnecessary tables
DROP TABLE IF EXISTS people CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- Drop and recreate show_team with correct schema
DROP TABLE IF EXISTS show_team CASCADE;

CREATE TABLE show_team (
    id BIGSERIAL PRIMARY KEY,
    title TEXT REFERENCES shows(title),
    name TEXT NOT NULL,
    role_type_id BIGINT REFERENCES role_types(id),
    team_order INTEGER,
    notes TEXT,
    search_name TEXT GENERATED ALWAYS AS (LOWER(name)) STORED,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT show_team_unique UNIQUE (title, name, role_type_id)
);

-- Reorder columns for better logical grouping
ALTER TABLE show_team
    ALTER COLUMN id SET NOT NULL, 
    ALTER COLUMN title SET NOT NULL, 
    ALTER COLUMN title SET NOT NULL, -- Core fields
    ALTER COLUMN role_type_id SET NOT NULL,
    ALTER COLUMN name SET NOT NULL,
    ALTER COLUMN search_name SET NOT NULL,
    ALTER COLUMN active SET NOT NULL DEFAULT true,
    ALTER COLUMN created_at SET NOT NULL DEFAULT NOW(),
    ALTER COLUMN updated_at SET NOT NULL DEFAULT NOW();

-- Add indexes for show_team
CREATE INDEX idx_show_team_title ON show_team(title);  -- Show lookups
CREATE INDEX idx_show_team_name ON show_team(name);  -- Exact matches
CREATE INDEX idx_show_team_search_name ON show_team(search_name);  -- Name search
CREATE INDEX idx_show_team_role_type_id ON show_team(role_type_id);  -- Role lookups

-- Add trigger for updated_at
CREATE TRIGGER update_show_team_updated_at
    BEFORE UPDATE ON show_team
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable RLS
ALTER TABLE show_team ENABLE ROW LEVEL SECURITY;

-- Add documentation
COMMENT ON TABLE show_team IS 'Creative team members associated with shows, with normalized roles';
COMMENT ON COLUMN show_team.name IS 'Name as credited, preserving original formatting';
COMMENT ON COLUMN show_team.role_type_id IS 'Reference to normalized role type';
