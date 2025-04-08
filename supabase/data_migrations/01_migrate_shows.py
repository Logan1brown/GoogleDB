#!/usr/bin/env python3
"""
Migration script to transfer show data from Google Sheets to Supabase.
Handles column name standardization and proper foreign key lookups.
"""

import os
from datetime import datetime
from typing import Dict, List, Tuple
import urllib.parse
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
print(f"Loading environment variables from: {env_path}")

# Set environment variables directly for testing
os.environ.update({
    'DATABASE_URL': 'postgresql://postgres:QTRlgAeCCO1fEumL@db.hlwnwcxylueaoemdqiwo.supabase.co:5432/postgres',
    'SUPABASE_URL': 'https://hlwnwcxylueaoemdqiwo.supabase.co'
})

# Also try loading from .env file
load_dotenv(env_path, override=True)

# Verify critical environment variables
required_vars = [
    'GOOGLE_SHEETS_SPREADSHEET_ID',
    'SHOWS_SHEET_NAME',
    'DATABASE_URL',
    'SUPABASE_URL'
]

print("\nChecking environment variables:")
for var in required_vars:
    value = os.getenv(var)
    masked_value = f"{value[:10]}..." if value else None
    print(f"- {var}: {masked_value}")
    if not value:
        raise ValueError(f"Missing required environment variable: {var}")

# Google Sheets Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
SHOWS_SHEET_NAME = os.getenv('SHOWS_SHEET_NAME')

# Supabase Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')

def get_google_sheets_service():
    """Initialize and return Google Sheets service using service account."""
    creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
    if not os.path.exists(creds_file):
        raise FileNotFoundError(f"Credentials file not found: {creds_file}")
        
    creds = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES)
    
    return build('sheets', 'v4', credentials=creds)

def get_shows_data(service) -> pd.DataFrame:
    """Get shows data from Google Sheets."""
    # Get spreadsheet ID and range
    SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    SHEET_NAME = os.getenv('SHOWS_SHEET_NAME')
    
    if not SPREADSHEET_ID or not SHEET_NAME:
        raise ValueError("Missing required environment variables")
    
    # Get data from sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:M"
    ).execute()
    
    values = result.get('values', [])
    if not values:
        raise ValueError('No data found in Google Sheets')
    
    headers = values[0]
    
    # Convert to DataFrame
    df = pd.DataFrame(values[1:], columns=headers)
    
    # Standardize column names
    column_mapping = {
        'shows': 'title',  # Main shows sheet
        'show_name': 'title',  # Show_team sheet
        'Title': 'title',  # TMDB_success_metrics
        'notes': 'description'
    }
    df = df.rename(columns=column_mapping)
    
    # Check for duplicate TMDB IDs
    tmdb_counts = df[df['TMDB_ID'].notna()]['TMDB_ID'].value_counts()
    duplicates = tmdb_counts[tmdb_counts > 1]
    if not duplicates.empty:
        print("\nWARNING: Found duplicate TMDB IDs:")
        for tmdb_id, count in duplicates.items():
            dupes = df[df['TMDB_ID'] == tmdb_id]
            print(f"\nTMDB ID {tmdb_id} appears {count} times in:")
            for _, row in dupes.iterrows():
                print(f"- {row['title']} (Network: {row['network']})")
    
    # Clean up data - strip whitespace
    for col in df.columns:
        df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) else None)
    
    print("\nColumns being imported:", ", ".join(df.columns))
    print(f"\nLoaded {len(df)} shows from spreadsheet")
    
    return df

def get_lookup_data(conn) -> Dict[str, Dict[str, int]]:
    """Get all lookup data (networks, studios, etc.) from Supabase."""
    lookups = {}
    tables = ['networks', 'genres', 'status_types', 
              'order_types', 'source_types']
    
    with conn.cursor() as cur:
        # Handle most tables normally
        for table in tables:
            cur.execute(f"SELECT id, name FROM {table}")
            # Create case-insensitive lookup map
            lookups[table] = {}
            lookups[table + '_lower'] = {}
            for row in cur.fetchall():
                lookups[table][row[1]] = row[0]  # Original case
                lookups[table + '_lower'][row[1].lower()] = row[0]  # Lowercase
        
        # Handle studios specially to include type
        cur.execute("SELECT id, name, type FROM studios")
        lookups['studios'] = {}
        lookups['studios_lower'] = {}
        lookups['studios_by_id'] = {}
        for row in cur.fetchall():
            lookups['studios'][row[1]] = {'id': row[0], 'type': row[2]}
            lookups['studios_lower'][row[1].lower()] = {'id': row[0], 'type': row[2]}
            lookups['studios_by_id'][row[0]] = {'name': row[1], 'type': row[2]}
    
    return lookups

def parse_studio_info(studio_str: str) -> tuple:
    """Parse studio string into studio name and production companies.
    Returns (studio_name, [production_companies])"""
    if pd.isna(studio_str) or not str(studio_str).strip():
        return None, []
        
    studio_str = str(studio_str).strip()
    
    # If it starts with 'Other:', parse out production companies
    if studio_str.startswith('Other:'):
        # Remove 'Other:' and split by comma or 'Other:'
        companies = [c.strip() for c in studio_str.replace('Other:', ',').split(',')]
        return None, [c for c in companies if c]  # Filter out empty strings
    
    return studio_str, []  # Return as potential studio name

def transform_show_data(df: pd.DataFrame, lookups: Dict[str, Dict[str, int]], conn: psycopg2.extensions.connection) -> List[tuple]:
    """Transform shows data to match Supabase schema."""
    # Validate required columns
    if 'title' not in df.columns:
        raise ValueError("Missing required 'title' column")
    
    transformed_data = []
    errors = []
    
    # Get default status ID (Development)
    default_status_id = lookups['status_types'].get('Development') or lookups['status_types_lower'].get('development')
    if not default_status_id:
        raise ValueError("Could not find default status 'Development' in status_types table")
    
    total_rows = len(df)
    for idx, (_, row) in enumerate(df.iterrows(), 1):
        if idx % 10 == 0:
            print(f"Processing {idx}/{total_rows} shows...")
            
        try:
            # Get title and description
            title = row['title'].strip()
            description = row['description'].strip() if pd.notna(row['description']) else None
            
            # Get status (default to Development if missing)
            status = row['status'].strip() if pd.notna(row['status']) else 'Development'
            if status not in lookups['status_types'] and status.lower() not in lookups['status_types_lower']:
                print(f"Warning: Missing status for show '{title}' - setting to 'Development'")
                status = 'Development'
            status_id = lookups['status_types'].get(status) or lookups['status_types_lower'].get(status.lower())
            
            # Get network (case-insensitive)
            network = row['network'].strip() if pd.notna(row['network']) else None
            network_id = None
            if network:
                if network in lookups['networks']:
                    network_id = lookups['networks'][network]
                elif network.lower() in lookups['networks_lower']:
                    network_id = lookups['networks_lower'][network.lower()]
            
            # Get studio (case-insensitive)
            studio = row['studio'].strip() if pd.notna(row['studio']) else None
            studio_id = None
            
            if studio:
                # Split on commas and 'Other:' to get individual companies
                companies = [c.strip() for c in studio.replace('Other:', '').split(',')]
                
                # Try to find a known studio in the list
                for company in companies:
                    company_info = None
                    if company in lookups['studios']:
                        company_info = lookups['studios'][company]
                    elif company.lower() in lookups['studios_lower']:
                        company_info = lookups['studios_lower'][company.lower()]
                    
                    if company_info:
                        # Use first company as the studio
                        if studio_id is None:
                            studio_id = company_info['id']
                    else:
                        # Insert new studio
                        with conn.cursor() as cur:
                            cur.execute(
                                """INSERT INTO studios (name, type) 
                                VALUES (%s, %s) 
                                ON CONFLICT (name) DO UPDATE 
                                SET type = EXCLUDED.type 
                                RETURNING id""",
                                (company, 'Production Company')
                            )
                            new_id = cur.fetchone()[0]
                            # Use first company as the studio
                            if studio_id is None:
                                studio_id = new_id
                            # Update lookups
                            lookups['studios'][company] = {'id': new_id, 'type': 'Production Company'}
                            lookups['studios_lower'][company.lower()] = {'id': new_id, 'type': 'Production Company'}
                            lookups['studios_by_id'][new_id] = {'name': company, 'type': 'Production Company'}
                            print(f"Added studio '{company}' with id {new_id}")
            
            # Get source type (case-insensitive)
            source_type = row['source_type'].strip() if pd.notna(row['source_type']) else None
            source_type_id = None
            if source_type:
                if source_type in lookups['source_types']:
                    source_type_id = lookups['source_types'][source_type]
                elif source_type.lower() in lookups['source_types_lower']:
                    source_type_id = lookups['source_types_lower'][source_type.lower()]
                if source_type_id is None:
                    print(f"Warning: Unknown source type '{source_type}' for show '{title}'")
            else:
                print(f"Warning: Missing source type for show '{title}'")
            
            # Get order type (case-insensitive)
            order_type = row['order_type'].strip() if pd.notna(row['order_type']) else None
            order_type_id = None
            if order_type:
                if order_type in lookups['order_types']:
                    order_type_id = lookups['order_types'][order_type]
                elif order_type.lower() in lookups['order_types_lower']:
                    order_type_id = lookups['order_types_lower'][order_type.lower()]
                if order_type_id is None:
                    print(f"Warning: Unknown order type '{order_type}' for show '{title}'")
            else:
                print(f"Warning: Missing order type for show '{title}'")
            

            
            # Get genre (case-insensitive)
            genre = row['genre'].strip() if pd.notna(row['genre']) else None
            genre_id = None
            if genre:
                if genre in lookups['genres']:
                    genre_id = lookups['genres'][genre]
                elif genre.lower() in lookups['genres_lower']:
                    genre_id = lookups['genres_lower'][genre.lower()]
            
            # Get subgenres (case-insensitive)
            subgenre = row['subgenre'].strip() if pd.notna(row['subgenre']) else None
            subgenre_ids = []
            if subgenre:
                for sg in subgenre.split(','):
                    sg = sg.strip()
                    if sg in lookups['genres']:
                        sg_id = lookups['genres'][sg]
                        subgenre_ids.append(sg_id)
                    elif sg.lower() in lookups['genres_lower']:
                        sg_id = lookups['genres_lower'][sg.lower()]
                        subgenre_ids.append(sg_id)
            
            # Get TMDB ID
            tmdb_id = int(row['TMDB_ID']) if pd.notna(row['TMDB_ID']) else None
            
            # Get date
            date = None
            if pd.notna(row['date']):
                try:
                    date_val = pd.to_datetime(row['date'])
                    if pd.notna(date_val):
                        date = date_val.date()
                    else:
                        print(f"Warning: Invalid date '{row['date']}' for show '{title}'")
                except:
                    print(f"Warning: Invalid date '{row['date']}' for show '{title}'")
            
            # Get episode count
            episode_count = None
            if pd.notna(row['episode_count']):
                try:
                    episode_count = int(row['episode_count'])
                except:
                    print(f"Warning: Invalid episode count '{row['episode_count']}' for show '{title}'")
            
            # Create tuple for insertion
            now = datetime.now()
            show_data = (
                title,  # title
                description,  # description
                status_id,  # status_id
                network_id,  # network_id
                studio_id,  # studio_id
                genre_id,  # genre_id
                subgenre_ids,  # subgenres
                source_type_id,  # source_type_id
                order_type_id,  # order_type_id
                date,  # date
                episode_count,  # episode_count
                tmdb_id,  # tmdb_id
                True,  # active
                now,  # created_at
                now  # updated_at
            )
            
            transformed_data.append(show_data)
            
            if len(transformed_data) % 10 == 0:
                print(f"Processing {len(transformed_data)}/{len(df)} shows...")
                
        except Exception as e:
            print(f"- Error processing show at row {idx + 1}: {str(e)}")
            continue
    
    if not transformed_data:
        raise ValueError("No valid shows to import")
    
    print(f"\nSuccessfully transformed {len(transformed_data)} shows")
    return transformed_data

def insert_shows_data(conn: psycopg2.extensions.connection, shows_data: List[Tuple]) -> None:
    """Insert shows data into the database."""
    cursor = conn.cursor()
    
    # Insert shows
    insert_query = """
    INSERT INTO shows (
        title, description, status_id, network_id, studio_id,
        genre_id, subgenres, source_type_id, order_type_id, date,
        episode_count, tmdb_id, active, created_at, updated_at
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    # Execute in batches of 100
    batch_size = 100
    for i in range(0, len(shows_data), batch_size):
        batch = shows_data[i:i + batch_size]
        cursor.executemany(insert_query, batch)
        print(f"Inserted {min(i + batch_size, len(shows_data))}/{len(shows_data)} shows...")
    
    cursor.close()

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
    """Main migration function."""
    print("Starting shows migration...\n")
    conn = None
    
    try:
        # Connect to Google Sheets
        print("Connecting to Google Sheets...")
        service = get_google_sheets_service()
        df = get_shows_data(service)
        print(f"Found {len(df)} shows in Google Sheets\n")
        
        # Connect to Supabase
        print("Connecting to Supabase...")
        conn = get_supabase_connection()
        
        # Get lookup data
        print("Getting lookup data...")
        lookups = get_lookup_data(conn)
        
        # Transform data
        print("Transforming data...")
        transformed_data = transform_show_data(df, lookups, conn)
        
        # Insert data
        print("\nInserting data into Supabase...")
        insert_shows_data(conn, transformed_data)
        
        # Commit the transaction
        conn.commit()
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"\nError during migration: {str(e)}")
        if conn is not None:
            print("Rolling back transaction...")
            conn.rollback()
        raise
    
        
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        # Get source data
        service = get_google_sheets_service()
        df = get_shows_data(service)
        print('\nSource data (first 50 rows):')
        print(df[['title', 'description', 'network', 'studio', 'genre', 'episode_count', 'source_type', 'status', 'order_type']].head(50).to_string())
    else:
        main()
