from supabase import Client, create_client
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get('SUPABASE_URL')
key: str = os.environ.get('SUPABASE_ANON_KEY')
supabase: Client = create_client(url, key)

def test_public_read():
    """Test that anonymous users can read data"""
    try:
        # Try reading from each table
        tables = ['network_list', 'studio_list', 'genre_list', 'shows']
        for table in tables:
            response = supabase.table(table).select("*").limit(1).execute()
            print(f"✅ Public read test passed for {table}")
            
    except Exception as e:
        print(f"❌ Public read test failed: {str(e)}")

def test_authenticated_insert():
    """Test that authenticated users can insert data"""
    try:
        # Sign in as test user (you'll need to create one in Supabase)
        auth = supabase.auth.sign_in_with_password({
            "email": "test@example.com",
            "password": "your-test-password"
        })
        
        # Try inserting test data
        response = supabase.table('shows').insert({
            "title": "Test Show (Delete Me)",
            "search_name": "test show delete me"
        }).execute()
        print("✅ Authenticated insert test passed")
        
    except Exception as e:
        print(f"❌ Authenticated insert test failed: {str(e)}")

def test_authenticated_update():
    """Test that authenticated users can update data"""
    try:
        # Update the test show we just created
        response = supabase.table('shows').update({
            "title": "Test Show Updated"
        }).eq("search_name", "test show delete me").execute()
        print("✅ Authenticated update test passed")
        
    except Exception as e:
        print(f"❌ Authenticated update test failed: {str(e)}")

def test_service_role_delete():
    """Test that service role can delete data"""
    try:
        # Create a new client with service role key
        admin_supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        
        # Delete our test data
        response = admin_supabase.table('shows').delete().eq(
            "search_name", "test show delete me"
        ).execute()
        print("✅ Service role delete test passed")
        
    except Exception as e:
        print(f"❌ Service role delete test failed: {str(e)}")

if __name__ == "__main__":
    print("Testing Supabase Policies...")
    test_public_read()
    test_authenticated_insert()
    test_authenticated_update()
    test_service_role_delete()
