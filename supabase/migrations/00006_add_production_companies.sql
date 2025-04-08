-- Add production_companies array to shows table and make studio_id optional
ALTER TABLE shows 
ADD COLUMN production_companies text[] DEFAULT '{}',
ALTER COLUMN studio_id DROP NOT NULL;

-- Add comments explaining the fields
COMMENT ON COLUMN shows.studio_id IS 'Reference to a known major studio from our studios lookup table';
COMMENT ON COLUMN shows.production_companies IS 'Array of production company names that are not in our studios lookup table';

-- Create indexes for better query performance
CREATE INDEX shows_production_companies_idx ON shows USING gin(production_companies);
CREATE INDEX shows_studio_id_idx ON shows(studio_id) WHERE studio_id IS NOT NULL;

-- Create a view that combines studio name with production companies for easier querying
CREATE OR REPLACE VIEW show_production_details AS
SELECT 
    s.id,
    s.title,
    st.name as studio_name,
    s.production_companies,
    CASE 
        WHEN st.name IS NULL AND array_length(s.production_companies, 1) > 0
        THEN s.production_companies[1]
        ELSE st.name
    END as primary_producer
FROM shows s
LEFT JOIN studios st ON s.studio_id = st.id;

COMMENT ON VIEW show_production_details IS 'Combines studio information with production companies for easier querying and display';
