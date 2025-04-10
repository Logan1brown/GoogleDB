#!/usr/bin/env python3
"""
Migration to import all lookup data from Google Sheets
"""
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config.sheets_config import sheets_config

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

def get_sheets_client() -> gspread.Client:
    """Get authenticated Google Sheets client."""
    load_dotenv()
    required_vars = ['GOOGLE_SHEETS_CREDENTIALS_FILE']
    for var in required_vars:
        if not os.getenv(var):
            print(f"Missing required environment variable: {var}")
            sys.exit(1)

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    credentials = Credentials.from_service_account_file(
        os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE'),
        scopes=scopes
    )
    
    return gspread.authorize(credentials)

def get_sheet_data(gc: gspread.Client, sheet_name: str) -> pd.DataFrame:
    """Get data from a specific Google Sheet."""
    spreadsheet = gc.open_by_key(sheets_config.spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)
    
    # Get all data including headers
    data = worksheet.get_all_values()
    
    # First row is headers
    headers = data[0]
    rows = data[1:]
    
    # Convert to DataFrame
    return pd.DataFrame(rows, columns=headers)

def clean_array_field(value: str) -> List[str]:
    """Clean and split array field values."""
    if pd.isna(value) or not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]

def import_networks(cur, network_df: pd.DataFrame):
    """Import networks from network_list sheet."""
    for _, row in network_df.iterrows():
        network = row['network']
        if pd.isna(network):
            continue
            
        aliases = clean_array_field(row.get('aliases', ''))
        
        cur.execute("""
            INSERT INTO network_list (network, type, parent_company, aliases)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (network) DO UPDATE SET
                type = EXCLUDED.type,
                parent_company = EXCLUDED.parent_company,
                aliases = EXCLUDED.aliases
        """, (
            network,
            row.get('type', 'Other'),
            row.get('parent_company'),
            aliases
        ))

def import_studios(cur, studio_df: pd.DataFrame):
    """Import studios from studio_list sheet."""
    for _, row in studio_df.iterrows():
        studio = row['studio']
        if pd.isna(studio):
            continue
            
        aliases = clean_array_field(row.get('aliases', ''))
        category = clean_array_field(row.get('category', ''))
        
        cur.execute("""
            INSERT INTO studio_list (
                studio, type, parent_company, division,
                platform, aliases, category
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (studio) DO UPDATE SET
                type = EXCLUDED.type,
                parent_company = EXCLUDED.parent_company,
                division = EXCLUDED.division,
                platform = EXCLUDED.platform,
                aliases = EXCLUDED.aliases,
                category = EXCLUDED.category
        """, (
            studio,
            row.get('type', 'Other'),
            row.get('parent_company'),
            row.get('division'),
            row.get('platform'),
            aliases,
            category
        ))

def import_genres(cur, genre_df: pd.DataFrame):
    """Import genres from genre_list sheet."""
    for _, row in genre_df.iterrows():
        genre = row['genre']
        if pd.isna(genre):
            continue
            
        aliases = clean_array_field(row.get('aliases', ''))
        
        cur.execute("""
            INSERT INTO genre_list (genre, category, aliases)
            VALUES (%s, %s, %s)
            ON CONFLICT (genre) DO UPDATE SET
                category = EXCLUDED.category,
                aliases = EXCLUDED.aliases
        """, (
            genre,
            row.get('category', 'Main'),
            aliases
        ))

def import_subgenres(cur, subgenre_df: pd.DataFrame):
    """Import subgenres from subgenre_list sheet."""
    for _, row in subgenre_df.iterrows():
        subgenre = row['subgenre']
        if pd.isna(subgenre):
            continue
            
        aliases = clean_array_field(row.get('aliases', ''))
        
        cur.execute("""
            INSERT INTO subgenre_list (subgenre, category, aliases)
            VALUES (%s, %s, %s)
            ON CONFLICT (subgenre) DO UPDATE SET
                category = EXCLUDED.category,
                aliases = EXCLUDED.aliases
        """, (
            subgenre,
            row.get('category', 'Main'),
            aliases
        ))

def import_status_types(cur, status_df: pd.DataFrame):
    """Import status types from status_types sheet."""
    for _, row in status_df.iterrows():
        status = row['status']
        if pd.isna(status):
            continue
            
        aliases = clean_array_field(row.get('aliases', ''))
        
        cur.execute("""
            INSERT INTO status_types (status, description, aliases)
            VALUES (%s, %s, %s)
            ON CONFLICT (status) DO UPDATE SET
                description = EXCLUDED.description,
                aliases = EXCLUDED.aliases
        """, (
            status,
            row.get('description'),
            aliases
        ))

def import_source_types(cur, source_df: pd.DataFrame):
    """Import source types from source_types sheet."""
    for _, row in source_df.iterrows():
        type_name = row['type']
        if pd.isna(type_name):
            continue
            
        aliases = clean_array_field(row.get('aliases', ''))
        
        cur.execute("""
            INSERT INTO source_types (type, category, aliases)
            VALUES (%s, %s, %s)
            ON CONFLICT (type) DO UPDATE SET
                category = EXCLUDED.category,
                aliases = EXCLUDED.aliases
        """, (
            type_name,
            row.get('category'),
            aliases
        ))

def import_role_types(cur, role_df: pd.DataFrame):
    """Import role types from role_types sheet."""
    for _, row in role_df.iterrows():
        role = row['role']
        if pd.isna(role):
            continue
            
        aliases = clean_array_field(row.get('aliases', ''))
        
        cur.execute("""
            INSERT INTO role_types (role, category, aliases)
            VALUES (%s, %s, %s)
            ON CONFLICT (role) DO UPDATE SET
                category = EXCLUDED.category,
                aliases = EXCLUDED.aliases
        """, (
            role,
            row.get('category', 'Other'),
            aliases
        ))

def import_order_types(cur, order_df: pd.DataFrame):
    """Import order types from order_types sheet."""
    for _, row in order_df.iterrows():
        type_name = row['type']
        if pd.isna(type_name):
            continue
            
        aliases = clean_array_field(row.get('aliases', ''))
        
        cur.execute("""
            INSERT INTO order_types (type, description, aliases)
            VALUES (%s, %s, %s)
            ON CONFLICT (type) DO UPDATE SET
                description = EXCLUDED.description,
                aliases = EXCLUDED.aliases
        """, (
            type_name,
            row.get('description'),
            aliases
        ))

def main():
    """Main migration function."""
    print("Starting lookup data import...")
    
    # Get database connection
    conn = get_supabase_connection()
    cur = conn.cursor()
    
    try:
        # Get Google Sheets client
        gc = get_sheets_client()
        
        # Import each lookup table
        sheets = {
            'network_list': import_networks,
            'studio_list': import_studios,
            'genre_list': import_genres,
            'subgenre_list': import_subgenres,
            'status_types': import_status_types,
            'source_types': import_source_types,
            'role_types': import_role_types,
            'order_types': import_order_types
        }
        
        for sheet_name, import_func in sheets.items():
            print(f"Importing {sheet_name}...")
            df = get_sheet_data(gc, sheet_name)
            import_func(cur, df)
            print(f"Finished importing {sheet_name}")
        
        # Commit all changes
        conn.commit()
        print("Successfully imported all lookup data")
        
    except Exception as e:
        print(f"Error during import: {e}")
        conn.rollback()
        raise
    
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
