-- Migration: Secure Materialized Views Access
-- Created: 2025-04-15

-- Revoke all access to materialized views from public roles
REVOKE ALL ON show_details FROM anon, public, authenticated;
REVOKE ALL ON network_stats FROM anon, public, authenticated;
REVOKE ALL ON team_summary FROM anon, public, authenticated;

-- Grant access only to service_role (which our secure API views use)
GRANT SELECT ON show_details TO service_role;
GRANT SELECT ON network_stats TO service_role;
GRANT SELECT ON team_summary TO service_role;

-- Ensure owner is postgres (or appropriate superuser)
ALTER MATERIALIZED VIEW show_details OWNER TO postgres;
ALTER MATERIALIZED VIEW network_stats OWNER TO postgres;
ALTER MATERIALIZED VIEW team_summary OWNER TO postgres;

-- Add comments explaining access pattern
COMMENT ON MATERIALIZED VIEW show_details IS 'Access restricted to service_role. Use api_show_details view for public/authenticated access.';
COMMENT ON MATERIALIZED VIEW network_stats IS 'Access restricted to service_role. Use api_network_stats view for authenticated access.';
COMMENT ON MATERIALIZED VIEW team_summary IS 'Access restricted to service_role. Use api_team_summary view for authenticated access.';
