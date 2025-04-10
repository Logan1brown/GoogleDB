#!/usr/bin/env python3
"""
Migration to populate studios array from sheets data
"""
import os
import sys
from typing import List
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def get_supabase_connection() -> connection:
    """Get connection to Supabase database."""
    load_dotenv()
    required_vars = ['DATABASE_URL']
    for var in required_vars:
        if not os.getenv(var):
            print(f"Missing required environment variable: {var}")
            sys.exit(1)
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.autocommit = False
    return conn

def get_sheets_data() -> pd.DataFrame:
    """Get data from Google Sheets."""
    # Import sheets config
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.config.sheets_config import sheets_config
    
    # Set up credentials
    creds = Credentials.from_service_account_file(
        sheets_config.get_credentials_path(),
        scopes=sheets_config.SCOPES
    )
    
    # Connect to sheets
    gc = gspread.authorize(creds)
    
    # Open spreadsheet and get shows sheet
    spreadsheet = gc.open_by_key(sheets_config.spreadsheet_id)
    shows_sheet = spreadsheet.worksheet(sheets_config.shows_sheet)
    
    # Get all data including headers
    data = shows_sheet.get_all_values()
    
    # First row is headers
    headers = data[0]
    rows = data[1:]
    
    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    return df

def get_studio_ids(studio_names: List[str], cur) -> List[int]:
    """Get studio IDs from studio_list table."""
    studio_ids = []
    for name in studio_names:
        name = name.strip()
        if name.startswith('Other: '):
            # Remove 'Other: ' prefix for lookup
            lookup_name = name[7:].strip()
        else:
            lookup_name = name
            
        cur.execute("SELECT id FROM studio_list WHERE name ILIKE %s", (lookup_name,))
        result = cur.fetchone()
        if result:
            studio_ids.append(result[0])
        else:
            print(f"Warning: Studio not found in studio_list: {lookup_name} (original: {name})")
    return studio_ids

def main():
    """Main migration function."""
    print("\nStarting migration to populate studios array...")
    
    # Connect to database
    conn = get_supabase_connection()
    
    try:
        # Get sheets data
        df = get_sheets_data()
        
        with conn.cursor() as cur:
            # Process each show
            for _, row in df.iterrows():
                title = row['shows']  # Using old column name
                studio_str = row['studio']
                
                if pd.isna(studio_str):
                    continue
                
                # Split studio string into list
                studio_names = [s.strip() for s in studio_str.split(',')]
                
                # Get studio IDs
                studio_ids = get_studio_ids(studio_names, cur)
                
                if studio_ids:
                    # Update show with studio IDs array
                    cur.execute("""
                        UPDATE shows 
                        SET studios = %s
                        WHERE title = %s
                    """, (studio_ids, title))
        
        # Commit transaction
        conn.commit()
        print("Migration completed successfully!")
    
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {str(e)}")
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == '__main__':
    main()
