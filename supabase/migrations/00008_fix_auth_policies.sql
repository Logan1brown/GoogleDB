-- Migration: Fix Auth Policies
-- Created: 2025-04-08

-- Drop existing policies
DROP POLICY IF EXISTS "Public can read network_list" ON network_list;
DROP POLICY IF EXISTS "Public can read studio_list" ON studio_list;
DROP POLICY IF EXISTS "Public can read genre_list" ON genre_list;
DROP POLICY IF EXISTS "Public can read subgenre_list" ON subgenre_list;
DROP POLICY IF EXISTS "Public can read shows" ON shows;
DROP POLICY IF EXISTS "Public can read show_team" ON show_team;
DROP POLICY IF EXISTS "Public can read tmdb_success_metrics" ON tmdb_success_metrics;

DROP POLICY IF EXISTS "Auth users can insert network_list" ON network_list;
DROP POLICY IF EXISTS "Auth users can update network_list" ON network_list;
DROP POLICY IF EXISTS "Auth users can insert studio_list" ON studio_list;
DROP POLICY IF EXISTS "Auth users can update studio_list" ON studio_list;
DROP POLICY IF EXISTS "Auth users can insert genre_list" ON genre_list;
DROP POLICY IF EXISTS "Auth users can update genre_list" ON genre_list;
DROP POLICY IF EXISTS "Auth users can insert subgenre_list" ON subgenre_list;
DROP POLICY IF EXISTS "Auth users can update subgenre_list" ON subgenre_list;
DROP POLICY IF EXISTS "Auth users can insert shows" ON shows;
DROP POLICY IF EXISTS "Auth users can update shows" ON shows;
DROP POLICY IF EXISTS "Auth users can insert show_team" ON show_team;
DROP POLICY IF EXISTS "Auth users can update show_team" ON show_team;
DROP POLICY IF EXISTS "Auth users can insert tmdb_success_metrics" ON tmdb_success_metrics;
DROP POLICY IF EXISTS "Auth users can update tmdb_success_metrics" ON tmdb_success_metrics;

DROP POLICY IF EXISTS "Admin users can delete network_list" ON network_list;
DROP POLICY IF EXISTS "Admin users can delete studio_list" ON studio_list;
DROP POLICY IF EXISTS "Admin users can delete genre_list" ON genre_list;
DROP POLICY IF EXISTS "Admin users can delete subgenre_list" ON subgenre_list;
DROP POLICY IF EXISTS "Admin users can delete shows" ON shows;
DROP POLICY IF EXISTS "Admin users can delete show_team" ON show_team;
DROP POLICY IF EXISTS "Admin users can delete tmdb_success_metrics" ON tmdb_success_metrics;

-- Create better policies

-- Network List policies
CREATE POLICY "Enable read for all users" ON network_list FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON network_list FOR INSERT WITH CHECK (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable update for authenticated users only" ON network_list FOR UPDATE USING (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable delete for admin only" ON network_list FOR DELETE USING (auth.role() = 'service_role');

-- Studio List policies
CREATE POLICY "Enable read for all users" ON studio_list FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON studio_list FOR INSERT WITH CHECK (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable update for authenticated users only" ON studio_list FOR UPDATE USING (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable delete for admin only" ON studio_list FOR DELETE USING (auth.role() = 'service_role');

-- Genre List policies
CREATE POLICY "Enable read for all users" ON genre_list FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON genre_list FOR INSERT WITH CHECK (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable update for authenticated users only" ON genre_list FOR UPDATE USING (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable delete for admin only" ON genre_list FOR DELETE USING (auth.role() = 'service_role');

-- Subgenre List policies
CREATE POLICY "Enable read for all users" ON subgenre_list FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON subgenre_list FOR INSERT WITH CHECK (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable update for authenticated users only" ON subgenre_list FOR UPDATE USING (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable delete for admin only" ON subgenre_list FOR DELETE USING (auth.role() = 'service_role');

-- Shows policies
CREATE POLICY "Enable read for all users" ON shows FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON shows FOR INSERT WITH CHECK (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable update for authenticated users only" ON shows FOR UPDATE USING (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable delete for admin only" ON shows FOR DELETE USING (auth.role() = 'service_role');

-- Show Team policies
CREATE POLICY "Enable read for all users" ON show_team FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON show_team FOR INSERT WITH CHECK (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable update for authenticated users only" ON show_team FOR UPDATE USING (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable delete for admin only" ON show_team FOR DELETE USING (auth.role() = 'service_role');

-- TMDB Success Metrics policies
CREATE POLICY "Enable read for all users" ON tmdb_success_metrics FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON tmdb_success_metrics FOR INSERT WITH CHECK (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable update for authenticated users only" ON tmdb_success_metrics FOR UPDATE USING (auth.role() IN ('authenticated', 'service_role'));
CREATE POLICY "Enable delete for admin only" ON tmdb_success_metrics FOR DELETE USING (auth.role() = 'service_role');
