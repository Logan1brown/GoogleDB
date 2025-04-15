"""Test anonymous access to Supabase views."""

import os
from supabase import create_client
import pandas as pd

def test_anon_access():
    """Test accessing views with anon key."""
    # Initialize Supabase client with anon key
    supabase = create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_ANON_KEY")
    )
    
    try:
        # Try accessing api_market_analysis
        print("\nTesting api_market_analysis...")
        response = supabase.table('api_market_analysis').select('*').execute()
        df = pd.DataFrame(response.data)
        print(f"✅ Success! Found {len(df)} rows in api_market_analysis")
        print(f"Columns: {', '.join(df.columns)}")
        
        # Try accessing underlying views
        print("\nTesting api_show_details...")
        response = supabase.table('api_show_details').select('*').execute()
        df = pd.DataFrame(response.data)
        print(f"✅ Success! Found {len(df)} rows in api_show_details")
        
        print("\nTesting api_network_stats...")
        response = supabase.table('api_network_stats').select('*').execute()
        df = pd.DataFrame(response.data)
        print(f"✅ Success! Found {len(df)} rows in api_network_stats")
        
        print("\nTesting api_team_summary...")
        response = supabase.table('api_team_summary').select('*').execute()
        df = pd.DataFrame(response.data)
        print(f"✅ Success! Found {len(df)} rows in api_team_summary")
        
        # Try accessing materialized views (should fail)
        print("\nTesting show_details (should fail)...")
        try:
            response = supabase.table('show_details').select('*').execute()
            print("❌ Error: Was able to access show_details with anon key!")
        except Exception as e:
            print("✅ Success! Cannot access show_details with anon key")
            print(f"Error (expected): {str(e)}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_anon_access()
