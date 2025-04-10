from supabase import Client, create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get connection details
DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Using service key for full access

print("Creating Supabase client...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    print("\n1. Testing basic connection...")
    response = supabase.table('shows').select('*', count='exact').limit(1).execute()
    print(f"✓ Connection successful! Found {response.count} total shows")
    
    print("\n2. Testing joins and filters...")
    response = supabase.table('shows')\
        .select('title, network:network_list(name)', count='exact')\
        .filter('title', 'ilike', '%the%')\
        .order('title')\
        .limit(3)\
        .execute()
    print("✓ Complex query successful! First 3 shows with 'the':")
    for show in response.data:
        print(f"  - {show['title']} ({show['network']['name'] if show['network'] else 'No network'})")
    
    print("\n3. Testing search by network...")
    response = supabase.table('shows')\
        .select('title, network_list!inner(name)')\
        .eq('network_list.name', 'Netflix')\
        .limit(3)\
        .execute()
    print("✓ Network search successful! First 3 Netflix shows:")
    for show in response.data:
        print(f"  - {show['title']}")

except Exception as e:
    print(f"\n❌ Error: {e}")
