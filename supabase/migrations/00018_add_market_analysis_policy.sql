-- Enable RLS for api_market_analysis
ALTER VIEW api_market_analysis OWNER TO authenticated;

-- Create policy to allow access to all users
CREATE POLICY market_analysis_policy ON api_market_analysis FOR ALL TO anon USING (true);

-- Grant access to authenticated users
GRANT ALL ON api_market_analysis TO authenticated;

-- Grant access to anon users
GRANT SELECT ON api_market_analysis TO anon;
