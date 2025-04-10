-- Migration: Add Studios Array
-- Created: 2025-04-09

-- Drop old studio_id column and add new studios array
ALTER TABLE shows 
    DROP COLUMN IF EXISTS studio_id,
    ADD COLUMN IF NOT EXISTS studios BIGINT[] DEFAULT '{}';

-- Add GIN index for studios array
CREATE INDEX IF NOT EXISTS idx_shows_studios ON shows USING GIN(studios);

-- Add comment
COMMENT ON COLUMN shows.studios IS 'Array of studio IDs, including both regular studios and production companies';
