#!/usr/bin/env python3
"""
Migration to populate production_company_ids from sheets data
"""
import os
import sys
from typing import List, Tuple
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
import pandas as pd

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
    # TODO: Use your existing sheets connection code here
    pass

def process_studio_string(studio_str: str, cur) -> Tuple[int, List[int]]:
    """Process studio string from sheets, returns (main_studio_id, [prodco_ids])."""
    studios = [s.strip() for s in studio_str.split(',')]
    main_studio_id = None
    prodco_ids = []
    
    for studio in studios:
        if studio.startswith('Other: '):
            # Production company
            name = studio[7:].strip()  # Remove 'Other: ' prefix
            # Check if exists
            cur.execute("SELECT id FROM studio_list WHERE name ILIKE %s", (name,))
            result = cur.fetchone()
            if result:
                prodco_ids.append(result[0])
            else:
                # Create new production company
                cur.execute(
                    "INSERT INTO studio_list (name, type) VALUES (%s, 'production company') RETURNING id",
                    (name,)
                )
                prodco_ids.append(cur.fetchone()[0])
        else:
            # Regular studio
            cur.execute("SELECT id FROM studio_list WHERE name ILIKE %s", (studio,))
            result = cur.fetchone()
            if result:
                if main_studio_id is None:  # First non-Other studio is main
                    main_studio_id = result[0]
                else:
                    prodco_ids.append(result[0])
    
    return main_studio_id, prodco_ids

def main():
    """Main migration function."""
    print("\nStarting migration to populate production company data...")
    
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
                
                # Process studios
                main_studio_id, prodco_ids = process_studio_string(studio_str, cur)
                
                # Update show
                cur.execute("""
                    UPDATE shows 
                    SET studio_id = %s,
                        production_company_ids = %s
                    WHERE title = %s
                """, (main_studio_id, prodco_ids, title))
        
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
