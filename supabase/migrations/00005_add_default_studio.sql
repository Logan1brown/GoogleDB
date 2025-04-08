-- Migration: Add default studio
-- Created: 2025-04-08

-- Insert default studio if it doesn't exist
INSERT INTO studios (name, type)
VALUES ('Unknown Studio', 'Studio')
ON CONFLICT (name) DO NOTHING;
