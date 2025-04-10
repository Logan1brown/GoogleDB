-- Migration: Update Shows Constraints
-- Created: 2025-04-09

-- Add NOT NULL constraint to network_id
ALTER TABLE shows ALTER COLUMN network_id SET NOT NULL;
