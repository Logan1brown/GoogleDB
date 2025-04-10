-- Migration: Create Lookup Tables
-- Created: 2025-04-09

-- Drop existing lookup tables if they exist
DROP TABLE IF EXISTS status_types CASCADE;
DROP TABLE IF EXISTS network_list CASCADE;
DROP TABLE IF EXISTS studio_list CASCADE;
DROP TABLE IF EXISTS genre_list CASCADE;
DROP TABLE IF EXISTS subgenre_list CASCADE;
DROP TABLE IF EXISTS source_types CASCADE;
DROP TABLE IF EXISTS role_types CASCADE;
DROP TABLE IF EXISTS order_types CASCADE;

-- Create status_types table
CREATE TABLE status_types (
    id BIGSERIAL PRIMARY KEY,
    status TEXT NOT NULL,
    description TEXT,
    aliases TEXT[],
    search_status TEXT GENERATED ALWAYS AS (LOWER(status)) STORED,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT status_types_status_unique UNIQUE (status),
    CONSTRAINT status_types_search_status_unique UNIQUE (search_status)
);

-- Create network_list table
CREATE TABLE network_list (
    id BIGSERIAL PRIMARY KEY,
    network TEXT NOT NULL,
    type TEXT NOT NULL,
    parent_company TEXT,
    aliases TEXT[],
    search_network TEXT GENERATED ALWAYS AS (LOWER(network)) STORED,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT network_list_network_unique UNIQUE (network),
    CONSTRAINT network_list_search_network_unique UNIQUE (search_network)
);

-- Create studio_list table
CREATE TABLE studio_list (
    id BIGSERIAL PRIMARY KEY,
    studio TEXT NOT NULL,
    type TEXT NOT NULL,
    parent_company TEXT,
    division TEXT,
    platform TEXT,
    aliases TEXT[],
    category TEXT[],
    search_studio TEXT GENERATED ALWAYS AS (LOWER(studio)) STORED,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT studio_list_studio_unique UNIQUE (studio),
    CONSTRAINT studio_list_search_studio_unique UNIQUE (search_studio)
);

-- Create genre_list table
CREATE TABLE genre_list (
    id BIGSERIAL PRIMARY KEY,
    genre TEXT NOT NULL,
    category TEXT NOT NULL,
    aliases TEXT[],
    search_genre TEXT GENERATED ALWAYS AS (LOWER(genre)) STORED,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT genre_list_genre_unique UNIQUE (genre),
    CONSTRAINT genre_list_search_genre_unique UNIQUE (search_genre)
);

-- Create subgenre_list table
CREATE TABLE subgenre_list (
    id BIGSERIAL PRIMARY KEY,
    subgenre TEXT NOT NULL,
    category TEXT NOT NULL,
    aliases TEXT[],
    search_subgenre TEXT GENERATED ALWAYS AS (LOWER(subgenre)) STORED,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT subgenre_list_subgenre_unique UNIQUE (subgenre),
    CONSTRAINT subgenre_list_search_subgenre_unique UNIQUE (search_subgenre)
);

-- Create source_types table
CREATE TABLE source_types (
    id BIGSERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    category TEXT,
    aliases TEXT[],
    search_type TEXT GENERATED ALWAYS AS (LOWER(type)) STORED,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT source_types_type_unique UNIQUE (type),
    CONSTRAINT source_types_search_type_unique UNIQUE (search_type)
);

-- Create role_types table
CREATE TABLE role_types (
    id BIGSERIAL PRIMARY KEY,
    role TEXT NOT NULL,
    category TEXT NOT NULL,
    aliases TEXT[],
    search_role TEXT GENERATED ALWAYS AS (LOWER(role)) STORED,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT role_types_role_unique UNIQUE (role),
    CONSTRAINT role_types_search_role_unique UNIQUE (search_role)
);

-- Create order_types table
CREATE TABLE order_types (
    id BIGSERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    description TEXT,
    aliases TEXT[],
    search_type TEXT GENERATED ALWAYS AS (LOWER(type)) STORED,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT order_types_type_unique UNIQUE (type),
    CONSTRAINT order_types_search_type_unique UNIQUE (search_type)
);

-- Add indexes for frequent lookups
CREATE INDEX idx_status_types_status ON status_types(status);
CREATE INDEX idx_status_types_search_status ON status_types(search_status);

CREATE INDEX idx_network_list_network ON network_list(network);
CREATE INDEX idx_network_list_search_network ON network_list(search_network);
CREATE INDEX idx_network_list_type ON network_list(type);
CREATE INDEX idx_network_list_parent_company ON network_list(parent_company);

CREATE INDEX idx_studio_list_studio ON studio_list(studio);
CREATE INDEX idx_studio_list_search_studio ON studio_list(search_studio);
CREATE INDEX idx_studio_list_type ON studio_list(type);
CREATE INDEX idx_studio_list_parent_company ON studio_list(parent_company);
CREATE INDEX idx_studio_list_platform ON studio_list(platform);
CREATE INDEX idx_studio_list_category ON studio_list USING GIN(category);

CREATE INDEX idx_genre_list_genre ON genre_list(genre);
CREATE INDEX idx_genre_list_search_genre ON genre_list(search_genre);
CREATE INDEX idx_genre_list_category ON genre_list(category);

CREATE INDEX idx_subgenre_list_subgenre ON subgenre_list(subgenre);
CREATE INDEX idx_subgenre_list_search_subgenre ON subgenre_list(search_subgenre);
CREATE INDEX idx_subgenre_list_category ON subgenre_list(category);

CREATE INDEX idx_source_types_type ON source_types(type);
CREATE INDEX idx_source_types_search_type ON source_types(search_type);
CREATE INDEX idx_source_types_category ON source_types(category);

CREATE INDEX idx_role_types_role ON role_types(role);
CREATE INDEX idx_role_types_search_role ON role_types(search_role);
CREATE INDEX idx_role_types_category ON role_types(category);

CREATE INDEX idx_order_types_type ON order_types(type);
CREATE INDEX idx_order_types_search_type ON order_types(search_type);

-- Add triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_status_types_updated_at
    BEFORE UPDATE ON status_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_network_list_updated_at
    BEFORE UPDATE ON network_list
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_studio_list_updated_at
    BEFORE UPDATE ON studio_list
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_genre_list_updated_at
    BEFORE UPDATE ON genre_list
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_subgenre_list_updated_at
    BEFORE UPDATE ON subgenre_list
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_source_types_updated_at
    BEFORE UPDATE ON source_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_role_types_updated_at
    BEFORE UPDATE ON role_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_order_types_updated_at
    BEFORE UPDATE ON order_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE status_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE network_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE genre_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE subgenre_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_types ENABLE ROW LEVEL SECURITY;

-- Add comments for documentation
COMMENT ON TABLE status_types IS 'Show status types (e.g., Active, Ended, Cancelled)';
COMMENT ON TABLE network_list IS 'TV Networks and streaming platforms';
COMMENT ON TABLE studio_list IS 'Production studios and companies';
COMMENT ON TABLE genre_list IS 'Primary show genres';
COMMENT ON TABLE subgenre_list IS 'Secondary show genres';
COMMENT ON TABLE source_types IS 'Show source material types (e.g., Original, Book, Comic)';
COMMENT ON TABLE role_types IS 'Creative and production role types';
COMMENT ON TABLE order_types IS 'Show order types (e.g., Limited, Ongoing, Pilot)';
