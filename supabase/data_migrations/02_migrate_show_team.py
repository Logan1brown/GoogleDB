#!/usr/bin/env python3

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def load_env_vars():
    """Load environment variables from .env file"""
    load_dotenv()
    
    required_vars = [
        'GOOGLE_SHEETS_SPREADSHEET_ID',
        'TEAM_SHEET_NAME',
        'DATABASE_URL',
        'SUPABASE_URL'
    ]
    
    print("\nChecking environment variables:")
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        # Print truncated version of sensitive values
        print(f"- {var}: {value[:10]}...")

def get_google_sheets_service():
    """Get authenticated Google Sheets service"""
    creds = Credentials.from_service_account_file(
        os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE'),
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    return build('sheets', 'v4', credentials=creds)

def get_show_team_data(service):
    """Get show team data from Google Sheets"""
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    sheet_name = os.getenv('TEAM_SHEET_NAME')
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A1:Z',
        valueRenderOption='UNFORMATTED_VALUE'
    ).execute()
    
    df = pd.DataFrame(result['values'][1:], columns=result['values'][0])
    print(f"\nColumns being imported: {', '.join(df.columns)}")
    print(f"\nLoaded {len(df)} show team entries from spreadsheet")
    return df

def get_db_connection():
    """Get connection to Supabase database"""
    print("\nConnecting to Supabase...")
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def get_lookup_data(conn):
    """Get lookup data from Supabase"""
    cursor = conn.cursor()
    lookups = {}

    # Get role types
    cursor.execute("""
        SELECT id, name
        FROM role_types;
    """)
    lookups['role_types'] = {}
    for row in cursor.fetchall():
        lookups['role_types'][row[1]] = row[0]

    cursor.close()
    return lookups



def transform_show_team_data(df, lookups):
    """Transform show team data for insertion"""
    print(f"\nStarting with {len(df)} rows")
    transformed_data = []
    role_errors = []
    skipped_shows = set()
    
    for _, row in df.iterrows():
        show_name = row['show_name']
        
        if not show_name or pd.isna(show_name):
            print(f"Skipping row with no show name: {row}")
            continue
        
        name = row['name'].strip() if pd.notna(row['name']) else None
        if not name:
            print(f"Warning: Missing name for show: {show_name}")
            continue
        
        # Handle roles
        roles = row['roles'] if pd.notna(row['roles']) else ''
        
        # Split roles by both comma and slash
        role_list = [r.strip() for r in roles.replace('/', ',').split(',') if r.strip()]
        
        # If no roles specified, use a default role
        if not role_list:
            print(f"Warning: No roles specified for {name} on {show_name}")
            role_list = ['Unknown']
        
        # Map each role
        valid_roles = []
        for role in role_list:
            role = role.strip().lower()
            # Handle common aliases
            role_map = {
                'w ep': 'Writer/Executive Producer',
                'wep': 'Writer/Executive Producer',
                'ep. sr': 'Showrunner',
                'd. ep': 'Director',
                'c': 'Creator',
                'w': 'Writer',
                'd': 'Director',
                'sr': 'Showrunner',
                'ep': 'Executive Producer',
                'p': 'Producer',
                'co-ep': 'Co-Producer',
                'coep': 'Co-Producer',
                'co ep': 'Co-Producer',
                'co-p': 'Co-Producer',
                'line-p': 'Line Producer',
                'co-sr': 'Co-Showrunner',
                'cp': 'Creative Producer',
                'actor': 'Actor',
                'writer': 'Writer',
                'director': 'Director',
                'showrunner': 'Showrunner',
                'executive producer': 'Executive Producer',
                'producer': 'Producer',
                'co-producer': 'Co-Producer',
                'line producer': 'Line Producer',
                'studio executive': 'Studio Executive',
                'network executive': 'Network Executive',
                'development executive': 'Development Executive',
                'host': 'Host',
                'co-showrunner': 'Co-Showrunner',
                'creative producer': 'Creative Producer',
                'creator': 'Creator',
                'unknown': 'Unknown'
            }
            role = role_map.get(role, role)
            if role not in lookups['role_types']:
                role_errors.append(f"{name} ({show_name}): Unknown role '{role}'")
                continue
            valid_roles.append(role)
            
        # If no valid roles found, use Unknown
        if not valid_roles:
            valid_roles = ['Unknown']
            
        # Add an entry for each valid role
        for role in valid_roles:
            role_id = lookups['role_types'][role]
            
            # Add to transformed data
            transformed_data.append({
                'title': show_name,
                'name': name,
                'role_type_id': role_id,
                'team_order': row['order'] if pd.notna(row['order']) else None,
                'notes': row['notes'] if pd.notna(row['notes']) else None
            })
    
    if role_errors:
        print("\nRole mapping errors:")
        for error in sorted(set(role_errors)):
            print(f"- {error}")
    
    return transformed_data

def insert_show_team_data(conn, data):
    """Insert show team data into Supabase"""
    print("\nInserting data into Supabase...")
    
    with conn.cursor() as cursor:
        # Insert in batches of 100
        batch_size = 100
        for i in range(0, len(data), batch_size):
            batch = [(item['title'], item['name'], item['role_type_id'], item['team_order'], item['notes']) for item in data[i:i + batch_size]]
            
            insert_query = """
                INSERT INTO show_team (title, name, role_type_id, team_order, notes)
                VALUES %s
                ON CONFLICT (title, name, role_type_id) DO NOTHING
                RETURNING id;
            """
            
            execute_values(cursor, insert_query, batch)
            print(f"Inserted {min(i + batch_size, len(data))}/{len(data)} show team entries...")

def main():
    """Main migration function"""
    print("Starting show team migration...")
    
    # Load environment variables
    load_env_vars()
    
    # Get source data from Google Sheets
    service = get_google_sheets_service()
    df = get_show_team_data(service)
    
    # Connect to database
    conn = get_db_connection()
    
    try:
        # Begin transaction
        conn.autocommit = False
        
        # Get lookup data
        lookups = get_lookup_data(conn)
        
        # Transform data
        transformed_data = transform_show_team_data(df, lookups)
        
        # Insert show team data
        insert_show_team_data(conn, transformed_data)
        
        # Commit transaction
        conn.commit()
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"\nError during migration: {str(e)}")
        print("\nRolling back transaction...")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        # Get source data
        service = get_google_sheets_service()
        df = get_show_team_data(service)
        print('\nSource data (first 50 rows):')
        print(df[['show_name', 'name', 'roles']].head(50).to_string())
    else:
        main()
