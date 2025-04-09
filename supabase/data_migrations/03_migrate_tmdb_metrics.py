#!/usr/bin/env python3
"""
Migration script to transfer TMDB metrics from Google Sheets to Supabase.
"""

import os
import sys
import json
import urllib.parse
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path, override=True)

def get_google_sheets_service():
    """Initialize and return Google Sheets service using service account."""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    # Get credentials file path from env
    creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
    if not creds_file:
        raise ValueError("Missing GOOGLE_SHEETS_CREDENTIALS_FILE environment variable")
    
    creds = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES)
    
    return build('sheets', 'v4', credentials=creds)

def get_tmdb_metrics_data(service) -> pd.DataFrame:
    """Get TMDB metrics data from Google Sheets."""
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    if not spreadsheet_id:
        raise ValueError("Missing GOOGLE_SHEETS_SPREADSHEET_ID environment variable")
    
    # Get metrics sheet name
    metrics_sheet = os.getenv('METRICS_SHEET_NAME', 'TMDB_success_metrics')
    
    # Get data from sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'{metrics_sheet}!A:H'
    ).execute()
    
    # Convert to DataFrame
    rows = result.get('values', [])
    if not rows:
        raise ValueError("No data found in sheet")
    
    headers = ['tmdb_id', 'title', 'seasons', 'episodes_per_season', 
              'total_episodes', 'average_episodes', 'status', 'last_air_date']
    df = pd.DataFrame(rows[1:], columns=headers)  # Skip header row
    
    # Convert types
    df['tmdb_id'] = pd.to_numeric(df['tmdb_id'], errors='coerce')
    df['seasons'] = pd.to_numeric(df['seasons'], errors='coerce')
    df['total_episodes'] = pd.to_numeric(df['total_episodes'], errors='coerce')
    df['average_episodes'] = pd.to_numeric(df['average_episodes'], errors='coerce')
    
    # Parse episodes per season into array
    df['episodes_per_season'] = df['episodes_per_season'].apply(
        lambda x: '{' + ','.join(str(int(e.strip())) for e in str(x).split(',') if e.strip().isdigit()) + '}'
        if pd.notna(x) else None
    )
    
    # Parse dates
    df['last_air_date'] = pd.to_datetime(df['last_air_date'], errors='coerce').dt.date
    
    return df

def get_status_mapping(conn: psycopg2.extensions.connection) -> Dict[str, int]:
    """Get mapping of status names to IDs."""
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM status_types;')
    status_types = cursor.fetchall()
    cursor.close()
    return {name: id for id, name in status_types}

def map_tmdb_status(tmdb_status: str) -> str:
    """Map TMDB status to our status type.
    
    Rules:
    - Returning Series -> Active
    - In Production -> Active
    - Ended -> Ended
    - Canceled/Cancelled -> Cancelled
    - Planned -> Development
    """
    if pd.isna(tmdb_status):
        return 'Unknown'
    
    mapping = {
        'Returning Series': 'Active',
        'In Production': 'Active',
        'Ended': 'Ended',
        'Canceled': 'Cancelled',
        'Cancelled': 'Cancelled',
        'Planned': 'Development'
    }
    return mapping.get(tmdb_status, 'Unknown')

def transform_tmdb_metrics_data(df: pd.DataFrame) -> List[Tuple]:
    """Transform TMDB metrics data for insertion."""
    print(f"\nStarting with {len(df)} rows")
    
    # Drop rows without TMDB ID
    df = df.dropna(subset=['tmdb_id'])
    print(f"Found {len(df)} rows with valid TMDB IDs")
    
    # Convert to list of tuples for insertion
    return [
        (
            int(row['tmdb_id']),
            int(row['seasons']) if pd.notna(row['seasons']) else None,
            row['episodes_per_season'],
            int(row['total_episodes']) if pd.notna(row['total_episodes']) else None,
            float(row['average_episodes']) if pd.notna(row['average_episodes']) else None,
            row['status'] if pd.notna(row['status']) else None,
            row['last_air_date'] if pd.notna(row['last_air_date']) else None
        )
        for _, row in df.iterrows()
    ]

def insert_tmdb_metrics_data(conn: psycopg2.extensions.connection, metrics_data: List[Tuple]):
    """Insert TMDB metrics data into the database."""
    cursor = conn.cursor()
    
    # Insert data in batches
    insert_query = """
        INSERT INTO tmdb_success_metrics (
            tmdb_id, seasons, episodes_per_season, total_episodes,
            average_episodes, status, last_air_date
        )
        VALUES %s
        ON CONFLICT (tmdb_id) DO UPDATE SET
            seasons = EXCLUDED.seasons,
            episodes_per_season = EXCLUDED.episodes_per_season,
            total_episodes = EXCLUDED.total_episodes,
            average_episodes = EXCLUDED.average_episodes,
            status = EXCLUDED.status,
            last_air_date = EXCLUDED.last_air_date,
            updated_at = NOW();
    """
    
    batch_size = 100
    for i in range(0, len(metrics_data), batch_size):
        batch = metrics_data[i:i + batch_size]
        execute_values(cursor, insert_query, batch)
        conn.commit()
        print(f"Inserted {min(i + batch_size, len(metrics_data))}/{len(metrics_data)} metrics...")
    
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
    print("Starting TMDB metrics migration...")
    
    # Get Google Sheets service
    service = get_google_sheets_service()
    print("Connected to Google Sheets")
    
    # Get connection to database
    conn = get_supabase_connection()
    print("Connected to database")
    
    try:
        # Get data from Google Sheets
        df = get_tmdb_metrics_data(service)
        print("Retrieved data from Google Sheets")
        
        # Transform data
        metrics_data = transform_tmdb_metrics_data(df)
        print("Transformed data")
        
        # Insert data
        insert_tmdb_metrics_data(conn, metrics_data)
        print("\nMigration complete!")
        
    except Exception as e:
        print(f"Error during migration: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
