-- Migration: Add Show Studios Junction Table
-- Created: 2025-04-09

-- Create Show Studios Junction Table
CREATE TABLE show_studio_links (
    id BIGSERIAL PRIMARY KEY,
    show_id BIGINT NOT NULL REFERENCES shows(id),
    studio_id BIGINT NOT NULL REFERENCES studios(id),
    is_primary BOOLEAN NOT NULL DEFAULT false,  -- Flag for primary studio
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT show_studio_unique UNIQUE (show_id, studio_id)
);

-- Add indexes
CREATE INDEX idx_show_studio_links_show_id ON show_studio_links(show_id);
CREATE INDEX idx_show_studio_links_studio_id ON show_studio_links(studio_id);
CREATE INDEX idx_show_studio_links_is_primary ON show_studio_links(is_primary);

-- Add trigger for updated_at
CREATE TRIGGER update_show_studio_links_updated_at
    BEFORE UPDATE ON show_studio_links
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE show_studio_links ENABLE ROW LEVEL SECURITY;

-- Comments
COMMENT ON TABLE show_studio_links IS 'Junction table linking shows to their studios (both primary and additional)';

-- Drop studio_id from shows since we'll use the junction table
ALTER TABLE shows DROP COLUMN studio_id;
