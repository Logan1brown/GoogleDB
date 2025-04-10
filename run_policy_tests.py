import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection string from env
DATABASE_URL = os.getenv('DATABASE_URL')

def run_test_sql():
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        print("Testing policies...")
        
        # Test 1: Public read access
        print("\n1. Testing public read access...")
        cursor.execute("SET ROLE anon; SELECT EXISTS (SELECT 1 FROM shows LIMIT 1);")
        result = cursor.fetchone()
        print(f"Can read as anon: {result[0]}")
        
        # Test 2: Anonymous insert (should fail)
        print("\n2. Testing anonymous insert (should fail)...")
        try:
            cursor.execute("""
                SET ROLE anon;
                INSERT INTO shows (title, search_name) 
                VALUES ('Test Show', 'test show');
            """)
            print("❌ Error: Anon insert succeeded when it should have failed")
        except psycopg2.Error as e:
            print("✅ Success: Anon insert properly denied")
        
        # Test 3: Authenticated insert
        print("\n3. Testing authenticated insert...")
        cursor.execute("""
            SET ROLE authenticated;
            INSERT INTO shows (title, search_name) 
            VALUES ('Test Show', 'test show')
            RETURNING id;
        """)
        test_id = cursor.fetchone()[0]
        print(f"✅ Success: Authenticated insert worked, created show with ID: {test_id}")
        
        # Test 4: Service role delete
        print("\n4. Testing service role delete...")
        cursor.execute("""
            SET ROLE service_role;
            DELETE FROM shows WHERE search_name = 'test show';
        """)
        print("✅ Success: Service role delete worked")
        
        # Commit changes
        conn.commit()
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_test_sql()
