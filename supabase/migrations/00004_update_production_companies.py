#!/usr/bin/env python3
"""
Migration to update production_companies to production_company_ids
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection

def get_supabase_connection() -> connection:
    """Get connection to Supabase database."""
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['DATABASE_URL']
    for var in required_vars:
        if not os.getenv(var):
            print(f"Missing required environment variable: {var}")
            sys.exit(1)
    
    # Connect to database
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.autocommit = False
    return conn

def main():
    """Main migration function."""
    print("\nStarting migration to update production companies...")
    
    # Connect to database
    conn = get_supabase_connection()
    
    try:
        with conn.cursor() as cur:
            # Drop old index first
            print("Dropping old index...")
            cur.execute("DROP INDEX IF EXISTS idx_shows_production_companies")
            
            # Rename and change type of column
            print("Updating column...")
            cur.execute("""
                ALTER TABLE shows 
                DROP COLUMN IF EXISTS production_companies,
                ADD COLUMN production_company_ids BIGINT[]
            """)
            
            # Add new index
            print("Creating new index...")
            cur.execute("CREATE INDEX idx_shows_production_company_ids ON shows USING GIN(production_company_ids)")
            
            # Commit transaction
            conn.commit()
            print("Migration completed successfully!")
            
    except Exception as e:
        print(f"\nError during migration: {str(e)}")
        print("\nRolling back transaction...")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
