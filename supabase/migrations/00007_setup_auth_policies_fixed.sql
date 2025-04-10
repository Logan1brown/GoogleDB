-- Migration: Setup Auth Policies
-- Created: 2025-04-08

-- First clean up any test data
DELETE FROM shows WHERE title LIKE 'test%';

-- Enable RLS on all tables
ALTER TABLE network_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE genre_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE subgenre_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE shows ENABLE ROW LEVEL SECURITY;
ALTER TABLE show_team ENABLE ROW LEVEL SECURITY;
ALTER TABLE tmdb_success_metrics ENABLE ROW LEVEL SECURITY;

-- Network List policies
CREATE POLICY "Allow public read access" ON network_list
    FOR SELECT TO public
    USING (true);

CREATE POLICY "Allow authenticated insert" ON network_list
    FOR INSERT TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated update" ON network_list
    FOR UPDATE TO authenticated
    USING (true);

CREATE POLICY "Allow service role delete" ON network_list
    FOR DELETE TO service_role
    USING (true);

-- Studio List policies (same pattern)
CREATE POLICY "Allow public read access" ON studio_list
    FOR SELECT TO public
    USING (true);

CREATE POLICY "Allow authenticated insert" ON studio_list
    FOR INSERT TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated update" ON studio_list
    FOR UPDATE TO authenticated
    USING (true);

CREATE POLICY "Allow service role delete" ON studio_list
    FOR DELETE TO service_role
    USING (true);

-- Genre List policies
CREATE POLICY "Allow public read access" ON genre_list
    FOR SELECT TO public
    USING (true);

CREATE POLICY "Allow authenticated insert" ON genre_list
    FOR INSERT TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated update" ON genre_list
    FOR UPDATE TO authenticated
    USING (true);

CREATE POLICY "Allow service role delete" ON genre_list
    FOR DELETE TO service_role
    USING (true);

-- Subgenre List policies
CREATE POLICY "Allow public read access" ON subgenre_list
    FOR SELECT TO public
    USING (true);

CREATE POLICY "Allow authenticated insert" ON subgenre_list
    FOR INSERT TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated update" ON subgenre_list
    FOR UPDATE TO authenticated
    USING (true);

CREATE POLICY "Allow service role delete" ON subgenre_list
    FOR DELETE TO service_role
    USING (true);

-- Shows policies
CREATE POLICY "Allow public read access" ON shows
    FOR SELECT TO public
    USING (true);

CREATE POLICY "Allow authenticated insert" ON shows
    FOR INSERT TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated update" ON shows
    FOR UPDATE TO authenticated
    USING (true);

CREATE POLICY "Allow service role delete" ON shows
    FOR DELETE TO service_role
    USING (true);

-- Show Team policies
CREATE POLICY "Allow public read access" ON show_team
    FOR SELECT TO public
    USING (true);

CREATE POLICY "Allow authenticated insert" ON show_team
    FOR INSERT TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated update" ON show_team
    FOR UPDATE TO authenticated
    USING (true);

CREATE POLICY "Allow service role delete" ON show_team
    FOR DELETE TO service_role
    USING (true);

-- TMDB Success Metrics policies
CREATE POLICY "Allow public read access" ON tmdb_success_metrics
    FOR SELECT TO public
    USING (true);

CREATE POLICY "Allow authenticated insert" ON tmdb_success_metrics
    FOR INSERT TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated update" ON tmdb_success_metrics
    FOR UPDATE TO authenticated
    USING (true);

CREATE POLICY "Allow service role delete" ON tmdb_success_metrics
    FOR DELETE TO service_role
    USING (true);
