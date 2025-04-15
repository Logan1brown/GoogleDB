-- Migration: Fix RLS on Tables
-- Created: 2025-04-15

-- Enable RLS on tmdb_success_metrics
ALTER TABLE public.tmdb_success_metrics ENABLE ROW LEVEL SECURITY;

-- Drop any existing policies
DROP POLICY IF EXISTS "Public can read tmdb_success_metrics" ON tmdb_success_metrics;
DROP POLICY IF EXISTS "Auth users can insert tmdb_success_metrics" ON tmdb_success_metrics;
DROP POLICY IF EXISTS "Auth users can update tmdb_success_metrics" ON tmdb_success_metrics;
DROP POLICY IF EXISTS "Admin users can delete tmdb_success_metrics" ON tmdb_success_metrics;

-- Create new policies for tmdb_success_metrics
-- Everyone can read
CREATE POLICY "Public can read tmdb_success_metrics" 
    ON public.tmdb_success_metrics
    FOR SELECT 
    USING (true);

-- Only authenticated users can insert
CREATE POLICY "Auth users can insert tmdb_success_metrics" 
    ON public.tmdb_success_metrics
    FOR INSERT 
    WITH CHECK (auth.role() IN ('authenticated', 'service_role'));

-- Only authenticated users can update
CREATE POLICY "Auth users can update tmdb_success_metrics" 
    ON public.tmdb_success_metrics
    FOR UPDATE 
    USING (auth.role() IN ('authenticated', 'service_role'));

-- Only admin/service_role can delete
CREATE POLICY "Admin users can delete tmdb_success_metrics" 
    ON public.tmdb_success_metrics
    FOR DELETE 
    USING (auth.role() = 'service_role');

-- Note: RLS cannot be enabled on materialized views
-- Security for materialized views is inherited from the source tables

