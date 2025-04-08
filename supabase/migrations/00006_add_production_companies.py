#!/usr/bin/env python3
"""
Migration to add production_companies array to shows table and make studio_id optional
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
    print("\nStarting migration to add production_companies and make studio_id optional...")
    
    # Connect to database
    conn = get_supabase_connection()
    
    try:
        with conn.cursor() as cur:
            # Add production_companies array and make studio_id optional
            print("Updating shows table...")
            cur.execute("""
                ALTER TABLE shows 
                ADD COLUMN IF NOT EXISTS production_company_ids BIGINT[] DEFAULT '{}',
                ALTER COLUMN description DROP NOT NULL,
                ALTER COLUMN studio_id DROP NOT NULL,
                ALTER COLUMN genre_id DROP NOT NULL,
                ALTER COLUMN source_type_id DROP NOT NULL,
                ALTER COLUMN order_type_id DROP NOT NULL,
                ALTER COLUMN status_id DROP NOT NULL,
                ALTER COLUMN tmdb_id DROP NOT NULL,
                DROP CONSTRAINT IF EXISTS shows_tmdb_id_key;
            """)
            
            # Add comments
            print("Adding column comments...")
            cur.execute("""
                COMMENT ON COLUMN shows.studio_id IS 'Reference to a known major studio from our studios lookup table';
                COMMENT ON COLUMN shows.production_company_ids IS 'Array of production company IDs from our studios lookup table';
            """)
            
            # Create indexes
            print("Creating indexes...")
            cur.execute("""
                CREATE INDEX IF NOT EXISTS shows_production_company_ids_idx ON shows USING gin(production_company_ids);
                CREATE INDEX IF NOT EXISTS shows_studio_id_idx ON shows(studio_id) WHERE studio_id IS NOT NULL;
            """)
            
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
