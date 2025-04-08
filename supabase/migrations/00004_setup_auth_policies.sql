-- Migration: Setup Auth Policies
-- Created: 2025-04-08

-- Rollback if needed
DROP TABLE IF EXISTS auth.user_metadata CASCADE;
DROP TYPE IF EXISTS user_role;
DROP SCHEMA IF EXISTS auth;

-- Create auth schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS auth;

-- Create a custom type for user roles
CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer');

-- Create a table to store additional user metadata
CREATE TABLE auth.user_metadata (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    role user_role NOT NULL DEFAULT 'viewer',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Add trigger for updated_at
CREATE TRIGGER update_user_metadata_updated_at
    BEFORE UPDATE ON auth.user_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable RLS on user_metadata
ALTER TABLE auth.user_metadata ENABLE ROW LEVEL SECURITY;

-- Policy for user_metadata: users can read their own metadata, admins can read all
CREATE POLICY "Users can read own metadata"
    ON auth.user_metadata
    FOR SELECT
    USING (
        auth.uid() = id 
        OR 
        EXISTS (
            SELECT 1 FROM auth.user_metadata um 
            WHERE um.id = auth.uid() AND um.role = 'admin'
        )
    );

-- Policy for user_metadata: only admins can update
CREATE POLICY "Only admins can update metadata"
    ON auth.user_metadata
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM auth.user_metadata um 
            WHERE um.id = auth.uid() AND um.role = 'admin'
        )
    );

-- Shows table policies
CREATE POLICY "Anyone can view active shows"
    ON shows
    FOR SELECT
    USING (active = true);

CREATE POLICY "Viewers can read active shows"
    ON shows
    FOR SELECT
    USING (
        active = true
        OR
        auth.role() = 'admin'
    );

CREATE POLICY "Editors and admins can insert shows"
    ON shows
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM auth.user_metadata um 
            WHERE um.id = auth.uid() AND um.role IN ('editor', 'admin')
        )
    );

CREATE POLICY "Editors and admins can update shows"
    ON shows
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM auth.user_metadata um 
            WHERE um.id = auth.uid() AND um.role IN ('editor', 'admin')
        )
    );

CREATE POLICY "Only admins can delete shows"
    ON shows
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM auth.user_metadata um 
            WHERE um.id = auth.uid() AND um.role = 'admin'
        )
    );

-- Show Team policies
CREATE POLICY "Show team members are viewable by authenticated users" ON show_team
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Show team members are insertable by editors" ON show_team
    FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1
            FROM auth.user_metadata um
            WHERE um.id = auth.uid()
            AND um.role IN ('editor', 'admin')
        )
    );

CREATE POLICY "Show team members are updatable by editors" ON show_team
    FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1
            FROM auth.user_metadata um
            WHERE um.id = auth.uid()
            AND um.role IN ('editor', 'admin')
        )
    );

CREATE POLICY "Show team members are deletable by editors" ON show_team
    FOR DELETE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1
            FROM auth.user_metadata um
            WHERE um.id = auth.uid()
            AND um.role IN ('editor', 'admin')
        )
    );

-- Team members table policies
CREATE POLICY "Anyone can view active team members"
    ON team_members
    FOR SELECT
    USING (active = true);

CREATE POLICY "Viewers can read active team members"
    ON show_team
    FOR SELECT
    USING (
        active = true
        OR
        auth.role() = 'admin'
    );

CREATE POLICY "Editors and admins can insert team members"
    ON team_members
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM auth.user_metadata um 
            WHERE um.id = auth.uid() AND um.role IN ('editor', 'admin')
        )
    );

CREATE POLICY "Editors can update active team members"
    ON show_team
    FOR UPDATE
    USING (
        active = true
        AND
        auth.role() IN ('admin', 'editor')
    )
    WITH CHECK (
        auth.role() IN ('admin', 'editor')
    );

CREATE POLICY "Editors and admins can update team members"
    ON team_members
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM auth.user_metadata um 
            WHERE um.id = auth.uid() AND um.role IN ('editor', 'admin')
        )
    );

CREATE POLICY "Only admins can delete team members"
    ON team_members
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM auth.user_metadata um 
            WHERE um.id = auth.uid() AND um.role = 'admin'
        )
    );

-- Support tables policies (networks, studios, genres, etc.)
DO $$ 
DECLARE
    table_name text;
BEGIN
    FOR table_name IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN (
            'networks', 'studios', 'genres', 'subgenres',
            'order_types', 'role_types', 'source_types', 'status_types'
        )
    LOOP
        EXECUTE format('
            CREATE POLICY "Anyone can view active %1$s"
                ON %1$s
                FOR SELECT
                USING (active = true);

            CREATE POLICY "Only admins can modify %1$s"
                ON %1$s
                FOR ALL
                USING (
                    EXISTS (
                        SELECT 1 FROM auth.user_metadata um 
                        WHERE um.id = auth.uid() AND um.role = ''admin''
                    )
                );
        ', table_name);
    END LOOP;
END $$;
