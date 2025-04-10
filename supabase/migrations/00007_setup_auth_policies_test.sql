-- Migration: Test Auth Policies
-- Created: 2025-04-08

-- Rollback if needed
DROP FUNCTION IF EXISTS test_as_anon CASCADE;
DROP FUNCTION IF EXISTS test_as_authenticated CASCADE;
DROP FUNCTION IF EXISTS test_as_service_role CASCADE;

-- Setup test helper functions
CREATE OR REPLACE FUNCTION test_as_anon()
RETURNS void AS $$
BEGIN
    SET LOCAL ROLE anon;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION test_as_authenticated()
RETURNS void AS $$
BEGIN
    SET LOCAL ROLE authenticated;
    -- Simulate JWT claims for an authenticated user
    SET LOCAL request.jwt.claim.sub = '00000000-0000-0000-0000-000000000000';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION test_as_service_role()
RETURNS void AS $$
BEGIN
    SET LOCAL ROLE service_role;
END;
$$ LANGUAGE plpgsql;

-- Test cases
DO $$ 
DECLARE
    test_show_id bigint;
    test_passed boolean := true;
    error_message text;
BEGIN
    -- Clean up any test data
    DELETE FROM shows WHERE title LIKE 'test_%';
    
    -- Test 1: Anonymous Read Access
    BEGIN
        PERFORM test_as_anon();
        IF NOT EXISTS (SELECT 1 FROM shows LIMIT 1) THEN
            test_passed := false;
            error_message := 'Anon read access failed';
            RAISE EXCEPTION 'Test failed: %', error_message;
        END IF;
        RAISE NOTICE 'Test 1 Passed: Anonymous read access works';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Test 1 Failed: %', error_message;
    END;

    -- Test 2: Anonymous Write Prevention
    BEGIN
        PERFORM test_as_anon();
        INSERT INTO shows (title) VALUES ('test_show')
        RETURNING id INTO test_show_id;
        
        test_passed := false;
        error_message := 'Anon write was allowed when it should be prevented';
        RAISE EXCEPTION 'Test failed: %', error_message;
    EXCEPTION WHEN insufficient_privilege THEN
        RAISE NOTICE 'Test 2 Passed: Anonymous write prevention works';
    END;

    -- Test 3: Authenticated Insert
    BEGIN
        PERFORM test_as_authenticated();
        INSERT INTO shows (title) VALUES ('test_show')
        RETURNING id INTO test_show_id;
        
        IF test_show_id IS NULL THEN
            test_passed := false;
            error_message := 'Authenticated insert failed';
            RAISE EXCEPTION 'Test failed: %', error_message;
        END IF;
        RAISE NOTICE 'Test 3 Passed: Authenticated insert works';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Test 3 Failed: %', error_message;
    END;

    -- Test 4: Authenticated Update
    BEGIN
        PERFORM test_as_authenticated();
        UPDATE shows 
        SET title = 'test_show_updated' 
        WHERE id = test_show_id;
        
        IF NOT EXISTS (SELECT 1 FROM shows WHERE id = test_show_id AND title = 'test_show_updated') THEN
            test_passed := false;
            error_message := 'Authenticated update failed';
            RAISE EXCEPTION 'Test failed: %', error_message;
        END IF;
        RAISE NOTICE 'Test 4 Passed: Authenticated update works';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Test 4 Failed: %', error_message;
    END;

    -- Test 5: Service Role Delete
    BEGIN
        PERFORM test_as_service_role();
        DELETE FROM shows WHERE id = test_show_id;
        
        IF EXISTS (SELECT 1 FROM shows WHERE id = test_show_id) THEN
            test_passed := false;
            error_message := 'Service role delete failed';
            RAISE EXCEPTION 'Test failed: %', error_message;
        END IF;
        RAISE NOTICE 'Test 5 Passed: Service role delete works';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Test 5 Failed: %', error_message;
    END;

    -- Cleanup
    DELETE FROM shows WHERE title LIKE 'test_%';
    
    IF test_passed THEN
        RAISE NOTICE 'All tests passed successfully!';
    END IF;
END $$;
