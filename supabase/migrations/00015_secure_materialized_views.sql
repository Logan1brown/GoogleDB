-- Migration: Secure Materialized Views
-- Created: 2025-04-15

-- Drop existing views if they exist
DROP VIEW IF EXISTS api_show_details CASCADE;
DROP VIEW IF EXISTS api_network_stats CASCADE;
DROP VIEW IF EXISTS api_team_summary CASCADE;

-- Revoke access to materialized views from public and authenticated roles
REVOKE ALL ON show_details FROM public, authenticated;
REVOKE ALL ON network_stats FROM public, authenticated;
REVOKE ALL ON team_summary FROM public, authenticated;

-- Create secure views with explicit SECURITY INVOKER
-- This ensures the view runs with the permissions of the calling user
CREATE VIEW public.api_show_details WITH (security_invoker = on) AS
SELECT 
    id,
    title,
    description,
    network_name,
    genre_name,
    subgenre_names,
    studio_names,
    status_name,
    order_type_name,
    source_type_name,
    date,
    episode_count,
    tmdb_id,
    tmdb_seasons,
    tmdb_total_episodes,
    tmdb_status,
    tmdb_last_air_date
FROM show_details;

CREATE VIEW public.api_network_stats WITH (security_invoker = on) AS
SELECT 
    network_id,
    network_name,
    total_shows,
    active_shows,
    ended_shows,
    genres,
    source_types
FROM network_stats;

CREATE VIEW public.api_team_summary WITH (security_invoker = on) AS
SELECT 
    show_id,
    show_title,
    writers,
    producers,
    directors,
    creators
FROM team_summary;

-- Grant access to the secure views
GRANT SELECT ON api_show_details TO authenticated;
GRANT SELECT ON api_network_stats TO authenticated;
GRANT SELECT ON api_team_summary TO authenticated;

-- Allow public read-only access to show_details only
GRANT SELECT ON api_show_details TO public;

-- Grant access to the materialized views to the view owner (service_role)
GRANT SELECT ON show_details TO service_role;
GRANT SELECT ON network_stats TO service_role;
GRANT SELECT ON team_summary TO service_role;

-- Update ShowsAnalyzer to use new views
COMMENT ON VIEW api_show_details IS 'Secure view for accessing show details. Use this instead of show_details materialized view directly.';
COMMENT ON VIEW api_network_stats IS 'Secure view for accessing network statistics. Use this instead of network_stats materialized view directly.';
COMMENT ON VIEW api_team_summary IS 'Secure view for accessing team information. Use this instead of team_summary materialized view directly.';
