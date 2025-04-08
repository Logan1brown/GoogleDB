-- Migration: Add Unknown role type
-- Created: 2025-04-08

-- Add Unknown role type
INSERT INTO role_types (name, search_name) VALUES ('Unknown', 'unknown')
ON CONFLICT (name) DO NOTHING;
