#!/usr/bin/env python3
"""Find shows that exist in sheets but not in database."""
import os
import sys
from dotenv import load_dotenv
import psycopg2
import gspread
from google.oauth2.service_account import Credentials

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config.sheets_config import sheets_config

def get_sheets_shows():
    """Get all shows from Google Sheets."""
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
    
    # Get all data
    data = shows_sheet.get_all_values()
    headers = data[0]
    shows_col = headers.index('shows')
    studio_col = headers.index('studio')
    
    # Return dict of show title -> studio
    return {
        row[shows_col]: row[studio_col]
        for row in data[1:]  # Skip header
        if row[shows_col]  # Only include non-empty shows
    }

def get_db_shows():
    """Get all shows from database."""
    load_dotenv()
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT title, studios FROM shows")
            return {row[0]: row[1] for row in cur.fetchall()}
    finally:
        conn.close()

def main():
    """Find missing shows."""
    print("\nFinding shows missing from database...")
    
    sheets_shows = get_sheets_shows()
    db_shows = get_db_shows()
    
    print(f"\nTotal shows in sheets: {len(sheets_shows)}")
    print(f"Total shows in database: {len(db_shows)}")
    
    missing_shows = []
    for title, studio in sheets_shows.items():
        if title not in db_shows:
            missing_shows.append((title, studio))
    
    print(f"\nMissing shows ({len(missing_shows)}):")
    for title, studio in sorted(missing_shows):
        print(f"- {title}")
        print(f"  Studios: {studio}")
        print()

if __name__ == '__main__':
    main()
