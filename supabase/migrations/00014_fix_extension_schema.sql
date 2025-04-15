-- Migration: Fix Extension Schema
-- Created: 2025-04-15

-- Create extensions schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS extensions;

-- Grant usage to public (needed for functions to work)
GRANT USAGE ON SCHEMA extensions TO public;

-- Drop dependent indexes
DROP INDEX IF EXISTS idx_shows_title_trgm;
DROP INDEX IF EXISTS idx_shows_search_title_trgm;
DROP INDEX IF EXISTS idx_show_team_name_trgm;
DROP INDEX IF EXISTS idx_show_team_search_name_trgm;
DROP INDEX IF EXISTS idx_show_details_title_trgm;

-- Move pg_trgm extension to extensions schema
DROP EXTENSION IF EXISTS pg_trgm CASCADE;
CREATE EXTENSION pg_trgm WITH SCHEMA extensions;

-- Update search_path to include extensions schema
-- Note: We use a DO block to get the current database name
DO $$
BEGIN
    EXECUTE format('ALTER DATABASE %I SET search_path TO "$user", public, extensions', current_database());
END
$$;

-- Recreate indexes using schema-qualified operator class
CREATE INDEX idx_shows_title_trgm ON shows USING gin (title extensions.gin_trgm_ops);
CREATE INDEX idx_shows_search_title_trgm ON shows USING gin (search_title extensions.gin_trgm_ops);
CREATE INDEX idx_show_team_name_trgm ON show_team USING gin (name extensions.gin_trgm_ops);
CREATE INDEX idx_show_team_search_name_trgm ON show_team USING gin (search_name extensions.gin_trgm_ops);
CREATE INDEX idx_show_details_title_trgm ON show_details USING gin (title extensions.gin_trgm_ops);
