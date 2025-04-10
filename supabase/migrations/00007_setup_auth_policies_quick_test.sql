-- Quick test for auth policies
-- Tests basic CRUD operations with different roles

-- Test 1: Anonymous read access
SET ROLE anon;
SELECT EXISTS (SELECT 1 FROM shows LIMIT 1) as anon_can_read;

-- Test 2: Anonymous write prevention
SET ROLE anon;
DO $$ 
BEGIN
    INSERT INTO shows (title) VALUES ('test_show');
    RAISE NOTICE 'ERROR: Anon write should be prevented';
EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'PASS: Anon write prevented as expected';
END $$;

-- Test 3: Authenticated insert
SET ROLE authenticated;
DO $$ 
BEGIN
    INSERT INTO shows (title) VALUES ('test_show')
    ON CONFLICT DO NOTHING;
    RAISE NOTICE 'PASS: Authenticated insert worked';
EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'ERROR: Authenticated insert failed';
END $$;

-- Test 4: Service role delete
SET ROLE service_role;
DELETE FROM shows WHERE title = 'test_show';
