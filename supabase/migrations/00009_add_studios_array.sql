-- Migration: Add Studios Array
-- Created: 2025-04-09

-- Rollback section
-- To rollback, run these commands:
/*
DROP INDEX IF EXISTS idx_shows_studios;
ALTER TABLE shows DROP COLUMN IF EXISTS studios;
*/

-- Forward migration
BEGIN;

-- Add studios array column
ALTER TABLE shows 
ADD COLUMN studios BIGINT[];

-- Create index for array operations
CREATE INDEX idx_shows_studios ON shows USING GIN(studios);

-- Add comment
COMMENT ON COLUMN shows.studios IS 'Array of studio IDs from studio_list (both studios and production companies)';

COMMIT;
