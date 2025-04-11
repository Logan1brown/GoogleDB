# Database Functions

## Overview

This document details the database functions, triggers, and extensions used in the Google Database.

## Core Functions

### Timestamp Management

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';
```

- Used by all tables to maintain `updated_at` timestamp
- Triggered before any UPDATE operation
- Cannot be overridden manually

### Text Search

The database uses pg_trgm for text similarity search:

1. **similarity(text, text) → real**
   - Returns similarity between two strings
   - Used for fuzzy matching show titles
   - Returns value between 0 (different) and 1 (identical)

2. **show_trgm(text) → text[]**
   - Shows trigrams in the given text
   - Useful for debugging search issues

3. **set_limit(real) → real**
   - Sets similarity threshold
   - Current setting: 0.3 (allows for typos)

## Triggers

### update_updated_at
```sql
CREATE TRIGGER update_updated_at
    BEFORE UPDATE ON table_name
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

Applied to tables:
- shows
- show_team
- network_list
- studio_list
- genre_list
- role_types
- status_types
- order_types
- source_types
- tmdb_success_metrics

### standardize_name
- Ensures consistent name formatting
- Preserves original capitalization
- Removes extra whitespace
- Applied to name fields in show_team

## Database Indexes

### Text Search Indexes

1. **Show Title Search**
```sql
-- Trigram indexes for fuzzy title search
CREATE INDEX idx_shows_title_trgm ON shows 
USING gin (title gin_trgm_ops);

CREATE INDEX idx_shows_search_title_trgm ON shows 
USING gin (search_title gin_trgm_ops);
```

2. **Team Member Search**
```sql
-- Trigram indexes for team member name search
CREATE INDEX idx_show_team_name_trgm ON show_team 
USING gin (name gin_trgm_ops);

CREATE INDEX idx_show_team_search_name_trgm ON show_team 
USING gin (search_name gin_trgm_ops);
```

### Array Field Indexes
```sql
-- GIN indexes for array fields
CREATE INDEX idx_shows_studios ON shows USING gin (studios);
CREATE INDEX idx_shows_subgenres ON shows USING gin (subgenres);
```

### Foreign Key Indexes
```sql
-- B-tree indexes for joins
CREATE INDEX idx_shows_network_id ON shows(network_id);
CREATE INDEX idx_shows_genre_id ON shows(genre_id);
CREATE INDEX idx_shows_status_id ON shows(status_id);
CREATE INDEX idx_shows_order_type_id ON shows(order_type_id);
CREATE INDEX idx_shows_source_type_id ON shows(source_type_id);
```

### Materialized View Indexes
```sql
-- Unique indexes for refreshing
CREATE UNIQUE INDEX idx_show_details_id ON show_details(id);
CREATE UNIQUE INDEX idx_team_summary_show_id ON team_summary(show_id);
CREATE UNIQUE INDEX idx_network_stats_id ON network_stats(network_id);

-- Performance indexes
CREATE INDEX idx_show_details_network ON show_details(network_name);
CREATE INDEX idx_show_details_status ON show_details(status_name);
CREATE INDEX idx_show_details_title_trgm ON show_details USING gin (title gin_trgm_ops);
```

## Generated Search Columns
```sql
-- Case-insensitive search fields
ALTER TABLE shows ADD COLUMN search_title text 
GENERATED ALWAYS AS (lower(title)) STORED;

ALTER TABLE show_team ADD COLUMN search_name text 
GENERATED ALWAYS AS (lower(name)) STORED;
```

### Search Query Example
```sql
SELECT title, similarity(search_title, lower($1)) as sml
FROM shows
WHERE search_title % $1  -- Uses GIN index
ORDER BY sml DESC, title;
```

## Extensions

1. **pg_trgm**
   - Powers text similarity search
   - Used for title matching
   - Enables fuzzy search

2. **btree_gin**
   - Supports GIN indexes on array fields
   - Used for studios and subgenres arrays

## Performance Considerations

1. **Index Usage**
   - GIN indexes for array fields
   - B-tree indexes for foreign keys
   - Text similarity indexes for search

2. **Trigger Overhead**
   - Minimal impact from timestamp triggers
   - Search field generation is async
   - Array operations use efficient indexes

## Maintenance

### Index Maintenance
```sql
REINDEX INDEX CONCURRENTLY idx_shows_title_trgm;
REINDEX INDEX CONCURRENTLY idx_shows_search_title_trgm;
```

### Statistics Updates
```sql
ANALYZE shows;
ANALYZE show_team;
```

Run these monthly or after large data changes.
