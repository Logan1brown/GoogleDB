-- Migration: Drop old studio_id column
-- Created: 2025-04-09

-- Rollback section
-- To rollback, run these commands:
/*
-- Recreate materialized view
CREATE MATERIALIZED VIEW show_details AS
-- Copy original view definition here

-- Add column and constraint
ALTER TABLE shows ADD COLUMN studio_id BIGINT;
ALTER TABLE shows ADD CONSTRAINT shows_studio_id_fkey FOREIGN KEY (studio_id) REFERENCES studio_list(id);
*/

-- Forward migration
BEGIN;

-- Drop materialized view first
DROP MATERIALIZED VIEW IF EXISTS show_details CASCADE;

-- Drop foreign key constraint
ALTER TABLE shows DROP CONSTRAINT IF EXISTS shows_studio_id_fkey;

-- Drop the column
ALTER TABLE shows DROP COLUMN IF EXISTS studio_id;

-- Recreate materialized view with new schema
CREATE MATERIALIZED VIEW show_details AS
SELECT 
    s.*,
    n.name AS network_name,
    sl.name AS studio_name,
    g.name AS genre_name,
    st.name AS status_name,
    srt.name AS source_type_name,
    ot.name AS order_type_name,
    array_agg(DISTINCT sgl.name) AS subgenre_names,
    array_agg(DISTINCT sl2.name) AS studio_names
FROM shows s
LEFT JOIN network_list n ON s.network_id = n.id
LEFT JOIN studio_list sl ON sl.id = ANY(s.studios)
LEFT JOIN genre_list g ON s.genre_id = g.id
LEFT JOIN status_types st ON s.status_id = st.id
LEFT JOIN source_types srt ON s.source_type_id = srt.id
LEFT JOIN order_types ot ON s.order_type_id = ot.id
LEFT JOIN UNNEST(s.subgenres) AS sg(id) ON true
LEFT JOIN subgenre_list sgl ON sg.id = sgl.id
LEFT JOIN studio_list sl2 ON sl2.id = ANY(s.studios)
GROUP BY 
    s.id, s.title, s.description, s.status_id, s.network_id,
    s.genre_id, s.source_type_id, s.order_type_id, s.date,
    s.episode_count, s.tmdb_id, s.active, s.created_at, s.updated_at,
    n.name, sl.name, g.name, st.name, srt.name, ot.name;

COMMIT;
