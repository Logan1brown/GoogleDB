#!/usr/bin/env python3
"""Add Unknown role type to Supabase."""

import os
import urllib.parse
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path, override=True)

def get_supabase_connection() -> psycopg2.extensions.connection:
    """Get connection to Supabase database."""
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("Missing DATABASE_URL environment variable")
    
    # Parse connection details from URL
    parsed = urllib.parse.urlparse(DATABASE_URL)
    dbname = parsed.path[1:]  # Remove leading slash
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port
    
    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

def main():
    """Add Unknown role type."""
    print("Adding Unknown role type...")
    conn = None
    
    try:
        # Connect to Supabase
        print("Connecting to Supabase...")
        conn = get_supabase_connection()
        cursor = conn.cursor()
        
        # Add Unknown role type
        cursor.execute("""
            INSERT INTO role_types (name)
            VALUES ('Unknown')
            ON CONFLICT (name) DO NOTHING
            RETURNING id;
        """)
        result = cursor.fetchone()
        
        if result:
            print(f"Added Unknown role type with ID: {result[0]}")
        else:
            print("Unknown role type already exists")
        
        conn.commit()
        print("\nMigration completed successfully!")
    
    except Exception as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.rollback()
        raise
    
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()
