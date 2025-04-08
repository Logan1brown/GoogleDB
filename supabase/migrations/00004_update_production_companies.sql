-- Migration: Update production_companies to production_company_ids
-- Created: 2025-04-08

-- Drop old index first
DROP INDEX IF EXISTS idx_shows_production_companies;

-- Rename and change type of column
ALTER TABLE shows 
DROP COLUMN IF EXISTS production_companies,
ADD COLUMN production_company_ids BIGINT[];

-- Add new index
CREATE INDEX idx_shows_production_company_ids ON shows USING GIN(production_company_ids);
