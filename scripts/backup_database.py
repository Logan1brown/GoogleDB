"""
Script to backup the Supabase database using the Python client.
"""

import json
from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

if not url or not key:
    raise ValueError("Missing Supabase credentials. Make sure SUPABASE_URL and SUPABASE_SERVICE_KEY are set in .env")

supabase: Client = create_client(url, key)

def backup_database():
    """Create a backup of all tables in the database"""
    backup = {}
    
    # List of tables to backup
    tables = [
        'shows',
        'network_list',
        'studio_list',
        'genre_list',
        'subgenre_list',
        'role_types',
        'show_team',
        'tmdb_success_metrics'
    ]
    
    # Fetch data from each table
    for table in tables:
        print(f"Backing up {table}...")
        response = supabase.table(table).select('*').execute()
        backup[table] = response.data
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    backup_file = f'backups/database_backup_{timestamp}.json'
    
    # Ensure backups directory exists
    os.makedirs('backups', exist_ok=True)
    
    # Write backup to file
    with open(backup_file, 'w') as f:
        json.dump(backup, f, indent=2, default=str)
    
    print(f"Backup completed successfully: {backup_file}")

if __name__ == '__main__':
    backup_database()
