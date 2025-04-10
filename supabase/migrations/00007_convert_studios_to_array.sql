-- Migration: Convert Studios to Array
-- Created: 2025-04-09

-- First create the new array column
ALTER TABLE shows 
ADD COLUMN studios BIGINT[];

-- Move existing studio_id values into the array
-- This puts the primary studio as the first element
UPDATE shows 
SET studios = ARRAY[studio_id]
WHERE studio_id IS NOT NULL;

-- Create index for array operations
CREATE INDEX idx_shows_studios ON shows USING GIN(studios);

-- Drop the old column
ALTER TABLE shows 
DROP COLUMN studio_id;

-- Add comment
COMMENT ON COLUMN shows.studios IS 'Array of studio IDs, first element is considered primary studio';
