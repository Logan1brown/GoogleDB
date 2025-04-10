-- Migration: Setup Auth Policies
-- Created: 2025-04-08

-- Enable RLS on all tables
ALTER TABLE network_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE genre_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE subgenre_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE shows ENABLE ROW LEVEL SECURITY;
ALTER TABLE show_team ENABLE ROW LEVEL SECURITY;
ALTER TABLE tmdb_success_metrics ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (read everything)
CREATE POLICY "Public can read network_list" ON network_list FOR SELECT USING (true);
CREATE POLICY "Public can read studio_list" ON studio_list FOR SELECT USING (true);
CREATE POLICY "Public can read genre_list" ON genre_list FOR SELECT USING (true);
CREATE POLICY "Public can read subgenre_list" ON subgenre_list FOR SELECT USING (true);
CREATE POLICY "Public can read shows" ON shows FOR SELECT USING (true);
CREATE POLICY "Public can read show_team" ON show_team FOR SELECT USING (true);
CREATE POLICY "Public can read tmdb_success_metrics" ON tmdb_success_metrics FOR SELECT USING (true);

-- Create policies for authenticated users (can add and edit)
CREATE POLICY "Auth users can insert network_list" ON network_list FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Auth users can update network_list" ON network_list FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Auth users can insert studio_list" ON studio_list FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Auth users can update studio_list" ON studio_list FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Auth users can insert genre_list" ON genre_list FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Auth users can update genre_list" ON genre_list FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Auth users can insert subgenre_list" ON subgenre_list FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Auth users can update subgenre_list" ON subgenre_list FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Auth users can insert shows" ON shows FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Auth users can update shows" ON shows FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Auth users can insert show_team" ON show_team FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Auth users can update show_team" ON show_team FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Auth users can insert tmdb_success_metrics" ON tmdb_success_metrics FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Auth users can update tmdb_success_metrics" ON tmdb_success_metrics FOR UPDATE USING (auth.role() = 'authenticated');

-- Create policies for admin users (full CRUD)
CREATE POLICY "Admin users can delete network_list" ON network_list FOR DELETE USING (auth.role() = 'service_role');
CREATE POLICY "Admin users can delete studio_list" ON studio_list FOR DELETE USING (auth.role() = 'service_role');
CREATE POLICY "Admin users can delete genre_list" ON genre_list FOR DELETE USING (auth.role() = 'service_role');
CREATE POLICY "Admin users can delete subgenre_list" ON subgenre_list FOR DELETE USING (auth.role() = 'service_role');
CREATE POLICY "Admin users can delete shows" ON shows FOR DELETE USING (auth.role() = 'service_role');
CREATE POLICY "Admin users can delete show_team" ON show_team FOR DELETE USING (auth.role() = 'service_role');
CREATE POLICY "Admin users can delete tmdb_success_metrics" ON tmdb_success_metrics FOR DELETE USING (auth.role() = 'service_role');
