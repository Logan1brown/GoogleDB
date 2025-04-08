-- Migration: Add production_companies column
-- Created: 2025-04-08

-- Add production_companies column to shows table
ALTER TABLE shows
ADD COLUMN production_companies TEXT[];

-- Add GIN index for array operations
CREATE INDEX idx_shows_production_companies ON shows USING GIN(production_companies);
