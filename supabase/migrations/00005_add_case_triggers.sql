-- Add triggers to standardize case in lookup tables
CREATE OR REPLACE FUNCTION standardize_name()
RETURNS trigger AS $$
BEGIN
    -- Convert first letter of each word to uppercase, rest to lowercase
    NEW.name = regexp_replace(
        initcap(NEW.name),
        '\s+(\w)',
        ' \1',
        'g'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger to each lookup table
CREATE TRIGGER standardize_network_name
    BEFORE INSERT OR UPDATE ON networks
    FOR EACH ROW
    EXECUTE FUNCTION standardize_name();

CREATE TRIGGER standardize_studio_name
    BEFORE INSERT OR UPDATE ON studios
    FOR EACH ROW
    EXECUTE FUNCTION standardize_name();

CREATE TRIGGER standardize_genre_name
    BEFORE INSERT OR UPDATE ON genres
    FOR EACH ROW
    EXECUTE FUNCTION standardize_name();

CREATE TRIGGER standardize_status_name
    BEFORE INSERT OR UPDATE ON status_types
    FOR EACH ROW
    EXECUTE FUNCTION standardize_name();

CREATE TRIGGER standardize_order_type_name
    BEFORE INSERT OR UPDATE ON order_types
    FOR EACH ROW
    EXECUTE FUNCTION standardize_name();

CREATE TRIGGER standardize_source_type_name
    BEFORE INSERT OR UPDATE ON source_types
    FOR EACH ROW
    EXECUTE FUNCTION standardize_name();

-- Update existing data to standardize case
UPDATE networks SET name = name;
UPDATE studios SET name = name;
UPDATE genres SET name = name;
UPDATE status_types SET name = name;
UPDATE order_types SET name = name;
UPDATE source_types SET name = name;
