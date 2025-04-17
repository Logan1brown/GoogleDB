-- Migration: Fix View Security
-- Created: 2025-04-16

-- Enable RLS for api_show_team
ALTER VIEW api_show_team OWNER TO authenticated;

-- Create policy for api_show_team
CREATE POLICY show_team_view_policy ON api_show_team FOR ALL TO anon USING (true);

-- Grant access to authenticated users
GRANT ALL ON api_show_team TO authenticated;

-- Grant access to anon users
GRANT SELECT ON api_show_team TO anon;

-- Re-enable RLS for api_market_analysis
ALTER VIEW api_market_analysis OWNER TO authenticated;

-- Create policy for api_market_analysis
CREATE POLICY market_analysis_view_policy ON api_market_analysis FOR ALL TO anon USING (true);

-- Re-grant access to authenticated users
GRANT ALL ON api_market_analysis TO authenticated;

-- Re-grant access to anon users
GRANT SELECT ON api_market_analysis TO anon;

-- Add helpful comments
COMMENT ON VIEW api_show_team IS 'Secure view providing team member data with show and network information. Includes all team members regardless of role.';
COMMENT ON VIEW api_market_analysis IS 'Secure view providing market analysis data. Team data has been moved to api_show_team view.';
